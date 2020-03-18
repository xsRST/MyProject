package com.genus.xs.multicast.afe.messages;


import com.genus.xs.multicast.afe.Utils;

public enum MessageType {
    LogonRequest(1), LogonResponse(2), AddWatch(3), DeleteWatch(4),
    Snapshot(5), DataPermission(6), ForceUpdate(8), Update(9),
    VerifySync(10), ClosingRun(11), Drop(12), IntraDayRebuild(13), IntraDayCorrection(14),
    ServerStatus(15), Alive(17), RaiseHandRequest(18), RaiseHandReply(19),
    SystemMessage(20), TemplateDefinition(21), TemplateData(22), TemplateRemove(23),
    TemplateCleanAll(24);


    private int value;

    MessageType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public byte getByteValue() {
        return Utils.int2bytes(value, 1)[0];
    }


    public static MessageType getByValue(int value) {
        for (MessageType type : values()) {
            if (value == type.getValue()) {
                return type;
            }
        }

        return null;
    }
}