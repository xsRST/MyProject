package com.genus.xs.multicast.handler;

import io.netty.buffer.ByteBuf;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.channel.socket.DatagramPacket;

import java.util.ArrayList;
import java.util.List;

public class MessageHandler extends SimpleChannelInboundHandler<DatagramPacket> {
    @Override
    protected void channelRead0(ChannelHandlerContext channelHandlerContext, DatagramPacket datagramPacket) throws Exception {
        ByteBuf in = datagramPacket.content();
        List<Byte> data = new ArrayList();
        while (in.readableBytes() > 0) {
            byte b = in.readByte();
            data.add(b);
        }
        System.out.println("data:" + data.toString());
    }
}
