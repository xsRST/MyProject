package com.genus.xs.multicast.client;

import com.genus.xs.multicast.handler.ClientMulticastHandler;
import io.netty.bootstrap.Bootstrap;
import io.netty.bootstrap.ChannelFactory;
import io.netty.buffer.Unpooled;
import io.netty.channel.Channel;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.ChannelOption;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.DatagramPacket;
import io.netty.channel.socket.InternetProtocolFamily;
import io.netty.channel.socket.nio.NioDatagramChannel;
import io.netty.util.NetUtil;
import org.apache.commons.lang.StringUtils;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;

public class MulticastClient {

    private InetSocketAddress groupAddress;
    private Channel ch;
    private static MulticastClient client;
    private static String localIp = "192.168.2.131";

    public MulticastClient(InetSocketAddress groupAddress) {
        this.groupAddress = groupAddress;
    }

    public void stop() {

        ch.close().awaitUninterruptibly();
    }

    public void send(int[] msg) {
        byte[] data = new byte[msg.length];
        for (int i = 0; i < msg.length; i++) {
            data[i] = (byte) (msg[i] & 0x00ff);
        }
        send(data);
    }

    private void send(List<Integer> list) {
        byte[] data = new byte[list.size()];
        for (int i = 0; i < list.size(); i++) {
            data[i] = (byte) (list.get(i) & 0x00ff);
        }
        send(data);
    }

    public void send(byte[] msg) {
        try {
            ch.writeAndFlush(new DatagramPacket(
                    Unpooled.copiedBuffer(msg),
                    groupAddress)).sync();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public void start() {
        EventLoopGroup group = new NioEventLoopGroup();
        NetworkInterface ni = NetUtil.LOOPBACK_IF;
        Enumeration<InetAddress> addresses = ni.getInetAddresses();
        InetAddress localAddress = null;
        while (addresses.hasMoreElements()) {
            InetAddress address = addresses.nextElement();
            if (address instanceof Inet4Address) {
                localAddress = address;
            }
        }

        Bootstrap b = new Bootstrap();
        b.group(group)
                .channelFactory((ChannelFactory<NioDatagramChannel>) () -> new NioDatagramChannel(InternetProtocolFamily.IPv4))
                .localAddress(localIp, groupAddress.getPort())
                .option(ChannelOption.IP_MULTICAST_IF, ni)
                .option(ChannelOption.SO_REUSEADDR, true)
                .handler(new ChannelInitializer<NioDatagramChannel>() {
                    @Override
                    public void initChannel(NioDatagramChannel ch) throws Exception {
                        ch.pipeline().addLast(new ClientMulticastHandler());
                    }
                });

        try {
            ch = b.bind().sync().channel();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }

    public static void main(String[] args) throws Exception {

        if (args.length > 0 && StringUtils.isNotEmpty(args[0])) {
            localIp = args[0];
        }
        InetSocketAddress groupAddress = new InetSocketAddress("233.36.26.128", 6628);
        client = new MulticastClient(groupAddress);
        client.start();
        //sendTest3Data();
        sendFile("E:\\工作\\工作\\09-交易所及行情\\AFE\\20191113.MulticastServer.log");
    }


    private static void sendTest3Data() {
        int[] bytes = {30, 15, 15, 233, 20, 0, 0, 0, 254, 184, 11, 233, 137, 244, 25, 100, 31, 15, 234, 22, 12, 0, 0, 0, 225, 41, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 244, 39, 15, 21, 22, 11, 0, 0, 0, 242, 42, 9, 0, 1, 255, 9, 54, 48, 48, 56, 49, 56, 46, 83, 83, 0, 1, 255, 7, 90, 72, 79, 78, 71, 76, 85, 0, 0, 255, 8, 214, 208, 194, 183, 185, 201, 183, 221, 0, 1, 255, 8, 45, 78, 239, 141, 161, 128, 253, 78, 0, 204, 51, 0, 0, 100, 0, 0, 0, 1, 255, 4, 69, 81, 84, 89, 0, 1, 255, 3, 67, 78, 89, 0, 78, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3};
        client.send(bytes);
    }


    private static void sendFile(String FileName) throws IOException, InterruptedException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(FileName)));
        while (true) {
            String line1 = reader.readLine();
            if (line1 == null) {
                break;
            }
            if (line1.startsWith("data:")) {
                for (String line : line1.split("data:")) {
                    if (null == line || line.trim().length() < 2) {
                        continue;
                    }
                    line = line.substring(1);
                    line = line.substring(0, line.length() - 1);
                    String[] ss = StringUtils.split(line, ",");
                    List<Integer> list = new ArrayList<>();
                    for (String s : ss) {
                        if (StringUtils.isNumeric(s.trim())) {
                            list.add(Integer.valueOf(s.trim()));
                        }
                    }
                    client.send(list);
                    Thread.sleep(500);
                }
            }
        }
        System.out.println("end test");
    }
}

