package com.genus.xs.multicast.afe;

import com.genus.xs.multicast.afe.messages.*;
import com.google.common.primitives.Bytes;
import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


/**
 * @author hfq
 * @date 2018/10/11
 */
public class Utils {
    private static final Logger logger = LoggerFactory.getLogger(Utils.class);

    public static final Charset defaultCharset = Charset.forName("ISO-8859-1");
    public static String[] prefix0 = {"", "0", "00", "000", "0000", "00000", "000000"};


    public static int b72int(byte[] bytes, int startPos) {
        if (bytes.length < 1 + startPos) {
            return 0;
        }
        if ((bytes[startPos] & 0x0001) > 0 && bytes.length > 1 + startPos) {
            return ((0x00fe & bytes[1 + startPos]) << 7) + (0x00ff & (bytes[startPos] >> 1));
        } else {
            return (bytes[startPos] & 0x00fe) >> 1;
        }
    }


    public static MessageType getMessageType(byte[] messageTypeValue) {
        byte messageType = (byte) (messageTypeValue[0] & 0x003f);
        return MessageType.getByValue(messageType);
    }

    public static byte[] uint2bytes(int num, int size) {
        if (size == 1) {
            byte[] bytes = new byte[1];
            bytes[0] = (byte) (num & 0x00ff);
            return bytes;
        } else if (size == 2) {
            byte[] bytes = new byte[2];
            bytes[1] = (byte) ((num >> 8) & 0x00ff);
            bytes[0] = (byte) (num & 0x00ff);
            return bytes;
        } else if (size == 4) {
            byte[] bytes = new byte[4];
            bytes[3] = (byte) ((num >> 24) & 0xff);
            bytes[2] = (byte) ((num >> 16) & 0xff);
            bytes[1] = (byte) ((num >> 8) & 0xff);
            bytes[0] = (byte) (num & 0xff);
            return bytes;
        } else {
            byte[] bytes = new byte[1];
            bytes[0] = (byte) (num & 0xff);
            return bytes;
        }
    }

    public static byte[] int2bytes(int num, int size) {
        if (num < 0) {
            byte[] b = uint2bytes(-num, size);
            b[size - 1] = (byte) (b[size - 1] | 0x80);
            return b;
        } else {
            return uint2bytes(num, size);
        }
    }

    public static int bytes2uint(byte[] bytes, int size, int startPos) {
        if (size == 1) {
            return (0x00ff & bytes[startPos]);
        } else if (size == 2) {
            return ((0x00ff & bytes[1 + startPos]) << 8) + (0x00ff & bytes[startPos]);
        } else if (size == 4) {
            return ((0x00ff & bytes[3 + startPos]) << 24) + ((0x00ff & bytes[2 + startPos]) << 16)
                    + ((0x00ff & bytes[1 + startPos]) << 8) + (0x00ff & bytes[startPos]);
        } else {
            return 0;
        }
    }


    public static byte[] long2bytes(long num, int size) {
        if (size == 8) {
            byte[] bytes = new byte[8];
            bytes[7] = (byte) ((num >> 56) & 0xff);
            bytes[6] = (byte) ((num >> 48) & 0xff);
            bytes[5] = (byte) ((num >> 40) & 0xff);
            bytes[4] = (byte) ((num >> 32) & 0xff);
            bytes[3] = (byte) ((num >> 24) & 0xff);
            bytes[2] = (byte) ((num >> 16) & 0xff);
            bytes[1] = (byte) ((num >> 8) & 0xff);
            bytes[0] = (byte) (num & 0xff);
            if (num < 0) {
                bytes[size - 1] = (byte) (bytes[size - 1] | 0x80);
                return bytes;
            }
            return bytes;
        } else {
            return int2bytes((int) num, size);
        }

    }

    public static byte[] getBytes(TransactionData data) {
        ByteBuffer byteBuffer = ByteBuffer.allocate(12);
        byte[] bytes = new byte[byteBuffer.limit()];
        byteBuffer.put(Utils.time2bytes(data.time));
        byteBuffer.put(Utils.long2bytes(data.vl, 4));
        byteBuffer.put(Utils.double2bytes(data.tp, 4, 3));
        byteBuffer.put(Utils.int2bytes(data.tradeType, 1));
        byteBuffer.flip();
        byteBuffer.get(bytes);
        return bytes;
    }

    public static String formatSymbol(String symbol, int expectLen) {
        int missNum = expectLen - symbol.trim().length();
        return missNum > 0 && missNum < 6 ? prefix0[missNum] + symbol : symbol;
    }

    public static TransactionData parseTransaction(byte[] bytes, int startPos) {
        TransactionData data = new TransactionData();
        data.vl = Utils.bytes2ulong(bytes, 8, startPos);
        data.tp = Utils.bytes2udouble(bytes, 4, 3, startPos + 8);
        data.tradeType = Utils.getChars(bytes, defaultCharset, startPos + 12, 1)[0];
        data.time = Utils.bytes2time(bytes, startPos + 13);
        return data;
    }

    public static String bytes2time(byte[] bytes, int startPos) {
        int v = bytes2uint(bytes, 4, startPos);
        String v1 = Integer.toString(v);
        StringBuilder sb = new StringBuilder();
        String hh = v1.substring(0, v1.length() - 4);
        String mm = v1.substring(v1.length() - 4, v1.length() - 2);
        String ss = v1.substring(v1.length() - 2, v1.length());
        sb.append(hh.length() == 1 ? "0" + hh : hh);
        sb.append(":").append(mm);
        sb.append(":").append(ss);
        return sb.toString();
    }

    public static String bytes2btime(byte[] bytes, int startPos) {
        StringBuilder sb = new StringBuilder();
        int hh = (bytes[startPos] & 0x00ff);
        int mm = (bytes[1 + startPos] & 0x00ff);
        int ss = (bytes[2 + startPos] & 0x00ff);
        sb.append(hh > 9 ? hh : "0" + hh);
        sb.append(mm > 9 ? mm : "0" + mm);
        sb.append(ss > 9 ? ss : "0" + ss);
        return sb.toString();
    }

    public static byte[] btime2bytes(String t) {
        int hh = Integer.parseInt(StringUtils.substring(t, 0, 2));
        int mm = Integer.parseInt(StringUtils.substring(t, 2, 4));
        int ss = Integer.parseInt(StringUtils.substring(t, 4, 6));
        ByteBuffer byteBuffer = ByteBuffer.allocate(3);
        byte[] bytes = new byte[byteBuffer.limit()];
        byteBuffer.put(int2bytes(hh, 1));
        byteBuffer.put(int2bytes(mm, 1));
        byteBuffer.put(int2bytes(ss, 1));
        byteBuffer.flip();
        byteBuffer.get(bytes);
        return bytes;
    }

    public static byte[] time2bytes(String t) {
        int time = Integer.parseInt(t);
        return int2bytes(time, 4);
    }

    public static String bytes2date(byte[] bytes, int startPos) {
        StringBuilder sb = new StringBuilder();
        sb.append(bytes2int(bytes, 2, startPos));
        int mm = (bytes[2 + startPos] & 0x00ff);
        int dd = (bytes[3 + startPos] & 0x00ff);
        sb.append(mm > 9 ? mm : "0" + mm);
        sb.append(dd > 9 ? dd : "0" + dd);
        return sb.toString();
    }

    public static byte[] date2bytes(String date) {
        int yyyy = Integer.parseInt(StringUtils.substring(date, 0, 4));
        int mm = Integer.parseInt(StringUtils.substring(date, 4, 6));
        int dd = Integer.parseInt(StringUtils.substring(date, 6, 8));
        ByteBuffer byteBuffer = ByteBuffer.allocate(4);
        byte[] bytes = new byte[byteBuffer.limit()];
        byteBuffer.put(int2bytes(yyyy, 2));
        byteBuffer.put(int2bytes(mm, 1));
        byteBuffer.put(int2bytes(dd, 1));
        byteBuffer.flip();
        byteBuffer.get(bytes);
        return bytes;

    }

    public static int bytes2int(byte[] bytes, int size, int startPos) {
        if ((bytes[startPos + size - 1] & 0x80) > 0) {
            byte[] d = Arrays.copyOfRange(bytes, 0, size);
            d[size - 1] = (byte) (d[size - 1] & 0x7f);
            return -bytes2uint(d, size, startPos);
        } else {
            return bytes2uint(bytes, size, startPos);
        }

    }

    public static byte[] string2CharArray(String s) {
        return string2CharArray(s, defaultCharset);
    }

    public static byte[] string2CharArray(String s, Charset charset) {
        byte[] data = s.getBytes(charset);
        ByteBuffer byteBuffer = ByteBuffer.allocate(data.length + 3);
        byte[] bytes = new byte[byteBuffer.limit()];
        byte b = new Byte("0");
        byteBuffer.put(b);
        byteBuffer.put(b);
        byte[] len = int2bytes(data.length, 1);
        byteBuffer.put(len);
        byteBuffer.put(data);
        byteBuffer.flip();
        byteBuffer.get(bytes);
        return bytes;
    }


    public static String charArray2String(byte[] bytes, Charset charset) {
        int len = bytes2uint(new byte[]{bytes[2]}, 1, 0);
        byte[] value = Arrays.copyOfRange(bytes, 3, len + 3);
        List<Byte> val = new ArrayList<>();
        for (int i = 0; value != null && i < value.length; i++) {
            if (0 != value[i]) {
                val.add(value[i]);
            }
        }
        String s = new String(Bytes.toArray(val), charset);
        logger.info(s);
        return s;
    }


    public static double bytes2float(byte[] bytes, int size, int decimalSize, int startPos) {
        int value = bytes2int(bytes, size, startPos);
        double val = value * Math.pow(0.1, decimalSize);
        return new BigDecimal(val).setScale(decimalSize, BigDecimal.ROUND_HALF_UP).doubleValue();

    }


    public static double bytes2double(byte[] bytes, int size, int decimalSize, int startPos) {
        long value = bytes2long(bytes, size, startPos);
        double val = value * Math.pow(0.1, decimalSize);
        return new BigDecimal(val).setScale(decimalSize, BigDecimal.ROUND_HALF_UP).doubleValue();

    }

    public static double bytes2udouble(byte[] bytes, int size, int decimalSize, int startPos) {
        long value = bytes2ulong(bytes, size, startPos);
        double val = value * Math.pow(0.1, decimalSize);
        return new BigDecimal(val).setScale(decimalSize, BigDecimal.ROUND_HALF_UP).doubleValue();

    }

    public static byte[] double2bytes(double d, int size, int decimalSize) {
        long value = (long) (d * Math.pow(10, decimalSize));
        return long2bytes(value, size);
    }

    public static long bytes2long(byte[] bytes, int size, int startPos) {
        if ((bytes[size - 1] & 0x80) > 0) {
            byte[] d = Arrays.copyOfRange(bytes, 0, size);
            d[size - 1] = (byte) (d[size - 1] & 0x7f);
            return -bytes2ulong(d, size, startPos);
        } else {
            return bytes2ulong(bytes, size, startPos);
        }
    }

    public static long bytes2ulong(byte[] bytes, int size, int startPos) {
        if (size == 1) {
            return (0x00ff & bytes[startPos]);
        } else if (size == 2) {
            return ((0x00ff & bytes[1 + startPos]) << 8) + (0x00ff & bytes[startPos]);
        } else if (size == 4) {
            return (((long) (0x00ff & bytes[3 + startPos]) << 24) + ((long) (0x00ff & bytes[2 + startPos]) << 16)
                    + ((long) (0x00ff & bytes[1 + startPos]) << 8) + (long) (0x00ff & bytes[startPos]));
        } else if (size == 8) {
            return ((long) (0x00ff & bytes[7 + startPos]) << 56) + ((long) (0x00ff & bytes[6 + startPos]) << 48)
                    + ((long) (0x00ff & bytes[5 + startPos]) << 40) + ((long) (0x00ff & bytes[4 + startPos]) << 32)
                    + ((long) (0x00ff & bytes[3 + startPos]) << 24) + ((long) (0x00ff & bytes[2 + startPos]) << 16)
                    + ((long) (0x00ff & bytes[1 + startPos]) << 8) + (0x00ff & bytes[startPos]);
        } else {
            return 0L;
        }
    }


    public static byte[] int2b7(int value) {
        byte high = (byte) (0x00ff & (value >> 7));
        byte low = (byte) (0x00fe & (value << 1));
        if (value > 127) {
            byte[] bytes = new byte[2];
            bytes[1] = high;
            bytes[0] = (byte) (low | 0x01);
            return bytes;
        } else {
            byte[] bytes = new byte[1];
            bytes[0] = low;
            return bytes;
        }

    }


    public static Message.Header parseHeader(final byte[] bytes, int startPos) {
        Message.Header header = new Message.Header();
        int bit1 = (int) ((bytes[startPos] >> 0) & 0x1);
        int length = bit1 == 1 ? 2 : 1;
        int position = startPos;
        header.setHeaderLength(6 + length);
        header.setMessageSize(Arrays.copyOfRange(bytes, position, position + length));
        position = position + length;
        bit1 = (int) ((bytes[position] >> 0) & 0x1);
        length = bit1 == 1 ? 2 : 1;
        header.setHeaderLength(header.getLength() + length);
        if (header.getMessageSize() == 0) {
            return null;
        }
        header.setSenderId(Arrays.copyOfRange(bytes, position, position + length));
        position = position + length;
        header.setSequenceNumber(Arrays.copyOfRange(bytes, position, position + 1));
        position = position + 1;
        header.setMessageType(Arrays.copyOfRange(bytes, position, position + 1));
        position = position + 1;
        header.setItemNumber(Arrays.copyOfRange(bytes, position, position + 4));
        return header;
    }

    public static byte[] getBytes(char[] chars) {
        return getBytes(chars, defaultCharset);
    }


    public static byte[] getBytes(char[] chars, Charset charset) {
        CharBuffer cb = CharBuffer.allocate(chars.length);
        cb.put(chars);
        cb.flip();
        ByteBuffer bb = charset.encode(cb);
        return bb.array();
    }


    public static char[] getChars(byte[] bytes, Charset charset, int startPos, int len) {
        ByteBuffer bb = ByteBuffer.allocate(len);
        bb.put(Arrays.copyOfRange(bytes, startPos, startPos + len));
        bb.flip();
        CharBuffer cb = charset.decode(bb);

        return cb.array();
    }


    public static void printBytes(byte[] bb) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < bb.length; i++) {
            sb.append(",").append(bb[i] & 0xff);
        }
        logger.info("data:{}", sb.toString());
    }

    public static DataType getFieldType(int fieldValue) {
        if (fieldValue <= 1000) {
            return DataType.AFEDataType.UINT8;
        } else if (fieldValue <= 2000) {
            return DataType.AFEDataType.UINT16;
        } else if (fieldValue <= 3000) {
            return DataType.AFEDataType.UINT32;
        } else if (fieldValue <= 4000) {
            return DataType.AFEDataType.UINT64;
        } else if (fieldValue <= 5000) {
            return DataType.AFEDataType.INT16;
        } else if (fieldValue <= 6000) {
            return DataType.AFEDataType.INT32;
        } else if (fieldValue <= 7000) {
            return DataType.AFEDataType.INT64;
        } else if (fieldValue <= 8000) {
            return DataType.AFEDataType.CharArray;
        } else if (fieldValue <= 9000) {
            return DataType.AFEDataType.MCharArray;
        } else if (fieldValue <= 9100) {
            return DataType.AFEDataType.TranX_D;
        } else if (fieldValue <= 9200) {
            return DataType.AFEDataType.TranX_D;
        } else if (fieldValue <= 9300) {
            return DataType.AFEDataType.BkrQue;
        } else if (fieldValue <= 9400) {
            return DataType.AFEDataType.Link;
        } else if (fieldValue <= 9500) {
            return DataType.AFEDataType.BTimeSec;
        } else if (fieldValue <= 9600) {
            return DataType.AFEDataType.BDateYear;
        } else if (fieldValue <= 11000) {
            return DataType.AFEDataType.UINT32_D3;
        } else if (fieldValue <= 12000) {
            return DataType.AFEDataType.UINT64_D4;
        } else if (fieldValue <= 13000) {
            return DataType.AFEDataType.INT32_D3;
        } else if (fieldValue <= 14000) {
            return DataType.AFEDataType.UINT64_D4;
        } else if (fieldValue <= 15000) {
            return DataType.AFEDataType.FieldList;
        } else if (fieldValue <= 16000) {
            return DataType.AFEDataType.UINT32_D4;
        } else if (fieldValue <= 17000) {
            return DataType.AFEDataType.INT32_D4;
        } else if (fieldValue <= 18000) {
            return DataType.AFEDataType.Char8;
        } else if (fieldValue == 18001) {
            return DataType.AFEDataType.PriceVolTran;
        } else if (fieldValue <= 20000) {
            return DataType.AFEDataType.INT64_D3;
        } else {
            return DataType.AFEDataType.UINT8;
        }
    }

    public static List<Message> handleMessageData(byte[] data) {
        int position = 0;
        List<Message> messages = new ArrayList<>();
        while (position < data.length) {
            Message.Header header = Utils.parseHeader(data, position);
            if (header == null) {
                break;
            }
            Message message = null;
            MessageType messageType = header.getMessageType();
            if (messageType != null) {
                switch (messageType) {
                    case IntraDayCorrection:
                        message = new NormalData();
                        break;
                    case TemplateDefinition:
                        message = new TemplateDefinition();
                        break;
                    case TemplateData:
                        message = new TemplateData();
                        break;
                    case TemplateRemove:
                        break;
                    case TemplateCleanAll:
                        break;
                    default:
                        message = new NormalData();
                        break;

                }
                if (message != null) {
                    message.setHeader(header);
                    message.parse(data, position);
                    messages.add(message);
                }
            }
            position = position + header.getMessageSize();

        }
        return messages;
    }
}
