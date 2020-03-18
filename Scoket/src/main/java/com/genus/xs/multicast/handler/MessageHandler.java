package com.genus.xs.multicast.handler;

import com.genus.xs.multicast.afe.Utils;
import com.genus.xs.multicast.afe.messages.Field;
import com.genus.xs.multicast.afe.messages.Message;
import com.genus.xs.multicast.afe.messages.MessageType;
import com.google.common.primitives.Bytes;
import io.netty.buffer.ByteBuf;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.channel.socket.DatagramPacket;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MessageHandler extends SimpleChannelInboundHandler<DatagramPacket> {
    private static final Logger logger = LoggerFactory.getLogger(MessageHandler.class);
    private String msgType = null;
    private Map<String, String> instrumentCodeMap = new HashMap<>();

    public MessageHandler(String msgType) {
        this.msgType = msgType;
    }

    @Override
    protected void channelRead0(ChannelHandlerContext channelHandlerContext, DatagramPacket datagramPacket) throws Exception {
        ByteBuf in = datagramPacket.content();
        List<Byte> data = new ArrayList();
        while (in.readableBytes() > 0) {
            byte b = in.readByte();
            data.add(b);
        }
        Boolean isTracked = false;
        try {
            List<Message> messages = Utils.handleMessageData(Bytes.toArray(data));
            for (Message message : messages) {
                isTracked = handleMessage(message) || isTracked;
            }
            if (isTracked) {
                Utils.printBytes(Bytes.toArray(data));
            }
        } catch (Exception e) {
        }
    }

    public boolean handleMessage(Message message) {
        boolean isTracked = false;
        Long instrumentNumber = message.getValue(Field.FieldDefinition.InstrumentNumber);

        if (message.getMessageType() == MessageType.Update) {
        }
        if (message.hasField(Field.FieldDefinition.EnglishShortName)) {
            if (instrumentNumber != null) {
                int symbolLength = 8;
                String instrumentCode = message.getValue(Field.FieldDefinition.InstrumentCode).toString().trim();

                if (message.hasField(Field.FieldDefinition.LotSize) == false) {
                    logger.warn("Can`t Find LotSize From Static {}", instrumentCode);
                } else {
                    String securityID = Long.toString(instrumentNumber).trim();
                    String exchange = "HK";
                    if (instrumentCode.endsWith("SS") || instrumentCode.endsWith("SZ")) {
                        symbolLength = 9;
                    }
                    instrumentCode = instrumentCode.split("\\.")[0] + "." + exchange;
                    instrumentCode = Utils.formatSymbol(instrumentCode, symbolLength);
                    securityID = Utils.formatSymbol(securityID, symbolLength - 3);
                    if (instrumentCodeMap.containsKey(instrumentNumber) == false) {
                        logger.info("Add new Static >>{} , {}", securityID, instrumentCode);
                        instrumentCodeMap.put(securityID, instrumentCode);
                        logger.info("handleMessage {}", message.toString());
                        isTracked = true;
                    }
                }
            }
        } else if (message.hasField(Field.FieldDefinition.DayLow)) {

        }
        return isTracked;

    }
}
