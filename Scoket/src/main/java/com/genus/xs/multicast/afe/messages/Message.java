package com.genus.xs.multicast.afe.messages;


import com.genus.xs.multicast.afe.Utils;
import org.apache.commons.math3.util.Pair;
import org.apache.mina.core.buffer.IoBuffer;

import java.nio.charset.Charset;
import java.util.*;

/**
 * @author hfq
 * @date 2018/10/11
 */
public abstract class Message {


    public abstract void parse(byte[] bytes, int startPos);

    public void setHeader(Header header) {
        this.header = header;
    }

    public void setMessageType(MessageType type) {
        header.setMessageType(type);
    }


    protected Header header = new Header();

    protected Map<Field, Object> data = new HashMap();
    protected List<Field> fieldList = new LinkedList<>();
    protected List<Pair<Field, Object>> dataList = new ArrayList<>();

    public void setItemNumber(int itemNumber) {
        header.setItemNumber(Utils.int2bytes(itemNumber, 4));
    }

    public Message() {
    }


    public void put(Field field, Object value) {
        data.put(field, value);
    }

    public Object get(Field field) {
        return data.get(field);
    }


    public <T> T getValue(Field field) {
        if (data.get(field) != null) {
            return (T) data.get(field);
        }
        return null;
    }

    public void addFieldList(Field field) {
        fieldList.add(field);
    }

    public void putFieldData(Field field, Object value) {
        dataList.add(new Pair<>(field, value));
    }

    public byte[] getBytes(Charset charset) {
        int size = 0;
        for (Field field : data.keySet()) {
            size = size + field.getBytes(data.get(field), charset).length;
        }
        if (fieldList.size() > 0) {
            size = size + fieldList.size() * 2 + 2;
        }
        header.setDataSize(size);
        IoBuffer byteBuffer = IoBuffer.allocate(header.getMessageSize()).setAutoExpand(true);

        byteBuffer.put(header.getBytes(charset));
        if (header.getMessageType() != MessageType.TemplateDefinition && header.getMessageType() != MessageType.TemplateData) {
            for (Field field : data.keySet()) {
                byteBuffer.put(Utils.int2bytes(field.getValue(), 2));
                byteBuffer.put(field.getBytes(data.get(field), charset));
            }
        }

        if (header.getMessageType() == MessageType.TemplateDefinition) {
            byteBuffer.put(Utils.int2bytes(fieldList.size(), 2));
            for (Field field : fieldList) {
                byteBuffer.put(Utils.int2bytes(field.getValue(), 2));
            }
        }
        if (header.getMessageType() == MessageType.TemplateData) {
            for (Pair<Field, Object> data : dataList) {
                byteBuffer.put(data.getKey().getBytes(data.getValue(), charset));
            }
        }


        byte[] bytes = new byte[byteBuffer.limit()];
        byteBuffer.flip();
        byteBuffer.get(bytes);
        return bytes;
    }

    public static class Header {


        protected int headerLength;

        protected byte[] messageSize;
        protected byte[] senderId = new byte[2];
        protected byte[] sequenceNumber = new byte[1];
        protected byte[] messageType = new byte[1];
        protected byte[] itemNumber = new byte[4];

        public int getLength() {
            return headerLength;
        }

        public void setHeaderLength(int headerLength) {
            this.headerLength = headerLength;
        }

        public void setDataSize(int dataSize) {
            headerLength = dataSize > 117 ? 10 : 9;
            messageSize = Utils.int2b7(dataSize + headerLength);
        }

        public byte[] getBytes(Charset charset) {
            IoBuffer byteBuffer = IoBuffer.allocate(headerLength).setAutoExpand(true);
            byteBuffer.put(messageSize);
            byteBuffer.put(senderId);
            byteBuffer.put(sequenceNumber);
            byteBuffer.put(messageType);
            byteBuffer.put(itemNumber);

            byte[] bytes = new byte[byteBuffer.limit()];
            byteBuffer.flip();
            byteBuffer.get(bytes);

            return bytes;
        }

        public long getItemNumber() {
            return Utils.bytes2ulong(itemNumber, 4, 0);
        }

        public void setItemNumber(byte[] itemNumber) {
            this.itemNumber = itemNumber;
        }


        public void setSenderId(byte[] senderId) {
            this.senderId = senderId;
        }

        public void setSenderId(int senderId) {
            this.senderId = Utils.int2b7(senderId);
        }


        public int getSequenceNumber() {
            return Utils.bytes2int(sequenceNumber, 1, 0);
        }

        public int getSenderId() {
            return Utils.bytes2int(senderId, senderId.length, 0) >> 3;
        }

        public void setSequenceNumber(byte[] sequenceNumber) {
            this.sequenceNumber = sequenceNumber;
            int num = getSequenceNumber();
        }


        public MessageType getMessageType() {
            return Utils.getMessageType(messageType);
        }

        public void setMessageType(byte[] messageType) {
            this.messageType = messageType;
        }

        public void setMessageType(MessageType messageType) {
            this.messageType[0] = (messageType.getByteValue());
        }

        public void setDataType(int dataType) {
            this.messageType[0] = (byte) (this.messageType[0] & 0x003f);
            this.messageType[0] = (byte) (this.messageType[0] + ((dataType << 6) & 0x00c0));
        }

        public int getMessageSize() {
            return Utils.b72int(messageSize, 0);
        }

        public void setMessageSize(byte[] messageSize) {
            this.messageSize = messageSize;
        }

    }

    public boolean hasField(Field field) {
        return data.containsKey(field);
    }

    public MessageType getMessageType() {
        return header.getMessageType();
    }


    @Override
    public String toString() {
        StringBuffer buffer = new StringBuffer("");
        buffer.append(header.getMessageType());
        buffer.append("@").append(header.getItemNumber());
        buffer.append("@ch").append(header.getSenderId());
        for (Field field : data.keySet()) {
            if (field != null) {
                buffer.append("[").append(field.getName()).append("=").append(data.get(field)).append("]");
            }
        }
        return buffer.toString();
    }
}
