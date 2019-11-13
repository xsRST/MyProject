package com.genus.xs.multicast.server;

import com.genus.xs.multicast.handler.MessageHandler;
import io.netty.bootstrap.Bootstrap;
import io.netty.channel.ChannelFactory;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.ChannelOption;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.InternetProtocolFamily;
import io.netty.channel.socket.nio.NioDatagramChannel;
import io.netty.util.NetUtil;

import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.util.Enumeration;

public class MulticastServer {

    private InetSocketAddress groupAddress;
    private String localIp;

//    public MulticastServer(InetSocketAddress groupAddress) {
//        this.groupAddress = groupAddress;
//    }

    public MulticastServer(InetSocketAddress groupAddress, String localIp) {
        this.groupAddress = groupAddress;
        this.localIp = localIp;
    }


    public void run() {
        EventLoopGroup group = new NioEventLoopGroup();
        try {
            NetworkInterface ni = localIp != null ? NetworkInterface.getByInetAddress(InetAddress.getByName(localIp)) : NetUtil.LOOPBACK_IF;
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
                    .localAddress(localAddress, groupAddress.getPort())
                    .option(ChannelOption.IP_MULTICAST_IF, ni)
                    .option(ChannelOption.SO_REUSEADDR, true)
                    .handler(new ChannelInitializer<NioDatagramChannel>() {
                        @Override
                        public void initChannel(NioDatagramChannel ch) throws Exception {
                            ch.pipeline().addLast(new MessageHandler());
                        }
                    });

            NioDatagramChannel ch = (NioDatagramChannel) b.bind(groupAddress.getPort()).sync().channel();
            ch.joinGroup(groupAddress, ni).sync();
            System.out.println("server start group = " + groupAddress);

            ch.closeFuture().await();

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            group.shutdownGracefully();
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("args:" + args);
        String localAddress = null;
        String address = "233.36.26.128";
        String groupPort = "6628";
        if (args.length == 3) {
            localAddress = args[0];
            address = args[1];
            groupPort = args[2];
        } else {
            System.exit(0);
        }
        System.out.println("localAddress:" + localAddress);
        System.out.println("address:" + address);
        System.out.println("groupPort:" + groupPort);
        String[] ports = groupPort.split(",");
        for (int i = 0; i < ports.length; i++) {

            String port = ports[i];
            String ip = address.split(",")[i];
            String localIp = localAddress.split(",").length == 1 ? localAddress : localAddress.split(",")[i];
            InetSocketAddress groupAddress = new InetSocketAddress(ip, Integer.parseInt(port));
            new Thread(() -> {
                new MulticastServer(groupAddress, localIp).run();
            }).start();
        }
    }
}