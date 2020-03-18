package com.genus.xs.multicast.afe.messages;


import com.genus.xs.multicast.afe.Utils;

import java.nio.charset.Charset;
import java.util.Arrays;

public interface DataType {

    int getValue();

    int getLength();

    DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset);

    byte[] getBytes(Object object, Charset charset);

    class DataTypeWrapper {

        public final int length;
        public final Object data;

        public DataTypeWrapper(int length, Object data) {
            this.length = length;
            this.data = data;
        }
    }

    enum AFEDataType implements DataType {
        UNKNOWN(-2, 0) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                return new DataTypeWrapper(0, 0);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return new byte[1];
            }

        },
        B7(-1, -1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.b72int(bytes, startPos);
                return new DataTypeWrapper(value > 127 ? 2 : 1, value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2b7((int) object);
            }

        }, UINT8(1, 1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2uint(bytes, 1, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 1);
            }
        }, UINT16(2, 2) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2uint(bytes, 2, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 2);
            }
        }, UINT32(3, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                long value = Utils.bytes2ulong(bytes, 4, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 4);
            }
        }, UINT64(4, 8) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                long value = Utils.bytes2ulong(bytes, 8, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.long2bytes((long) object, 8);
            }
        }, INT16(5, 2) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2int(bytes, 2, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 2);
            }
        }, INT32(6, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2int(bytes, 4, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 4);
            }
        }, INT64(7, 8) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                long value = Utils.bytes2long(bytes, 8, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.long2bytes((long) object, 8);
            }
        }, UINT32_D4(8, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2udouble(bytes, 4, 4, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 4, 4);
            }
        }, UINT32_D3(8, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2udouble(bytes, 4, 3, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 4, 3);
            }
        }, UINT64_D4(9, 8) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2udouble(bytes, 8, 4, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 8, 4);
            }
        },
        INT32_D3(10, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2float(bytes, 4, 3, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 4, 3);
            }
        }, INT64_D4(11, 8) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2double(bytes, 8, 4, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 8, 4);
            }
        }, CharArray(12, -1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
//                String value = Utils.charArray2String(bytes, charset);
                int len = Utils.bytes2uint(bytes, 1, startPos + 2);

                byte[] value = Arrays.copyOfRange(bytes, startPos + 3, startPos + len + 3);
                String s = new String(value, charset);
                return new DataTypeWrapper(len + 4, s);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.string2CharArray((String) object, charset);
            }
        }, MCharArray(13, -1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2int(bytes, 1, startPos);
                return new DataTypeWrapper(2, value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 4);
            }
        }, TranX_D(14, -1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2int(bytes, 1, startPos);
                return new DataTypeWrapper(2, value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 4);
            }
        }, BTimeSec(15, 3) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                String value = Utils.bytes2btime(bytes, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.btime2bytes((String) object);
            }
        }, BDateYear(16, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                String value = Utils.bytes2date(bytes, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.date2bytes((String) object);
            }
        }, BkrQue(17, -1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2int(bytes, 1, startPos);
                return new DataTypeWrapper(2, value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 4);
            }
        }, Link(18, -1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2int(bytes, 1, startPos);
                return new DataTypeWrapper(2, value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 4);
            }
        }, FieldList(19, -1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                int value = Utils.bytes2int(bytes, 1, startPos);
                return new DataTypeWrapper(2, value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.int2bytes((int) object, 4);
            }
        }, Char8(20, 1) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                char[] value = Utils.getChars(bytes, charset, startPos, 1);
                return new DataTypeWrapper(1, value[0]);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.getBytes(((String) object).toCharArray());
            }
        }, UNIT32_D4(21, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2udouble(bytes, 4, 4, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 4, 4);
            }
        }, INT32_D4(22, 4) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2double(bytes, 4, 4, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 4, 4);
            }
        }, PriceVolTran(23, 17) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                TransactionData data = Utils.parseTransaction(bytes, startPos);
                return new DataTypeWrapper(getLength(), data);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.getBytes((TransactionData) object);
            }
        }, INT64_D3(24, 8) {
            @Override
            public DataTypeWrapper parse(byte[] bytes, int startPos, Charset charset) {
                double value = Utils.bytes2double(bytes, 8, 3, startPos);
                return new DataTypeWrapper(getLength(), value);
            }

            @Override
            public byte[] getBytes(Object object, Charset charset) {
                return Utils.double2bytes((double) object, 8, 4);
            }
        };


        private final int value;
        private final int length;

        AFEDataType(int value, int length) {
            this.length = length;
            this.value = value;
        }


        @Override
        public int getValue() {
            return value;
        }

        @Override
        public int getLength() {
            return length;
        }

        public static AFEDataType resolve(int value) {
            for (AFEDataType type : values()) {
                if (value == type.getValue()) {
                    return type;
                }
            }

            return null;
        }
    }

}