package com.genus.xs.multicast.afe.messages;

import com.genus.xs.multicast.afe.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @author hfq
 * @date 2018/10/19
 */
public class NormalData extends Message {
    private static final Logger logger = LoggerFactory.getLogger(NormalData.class);

    @Override
    public void parse(byte[] bytes, int startPos) {
        if (header == null) {
            return;
        }
        int position = header.getLength() + startPos;
        while (position < header.getMessageSize() + startPos && position < bytes.length) {
            int fieldValue = Utils.bytes2uint(bytes, 2, position);
            Field field = Field.FieldDefinition.resolve(fieldValue);
            DataType.DataTypeWrapper value;
            position = position + 2;

            if (field == null) {
                DataType dataType = Utils.getFieldType(fieldValue);
                value = dataType.parse(bytes, position, Utils.defaultCharset);
                position = position + value.length;
            } else {
                value = (DataType.DataTypeWrapper) field.parse(bytes, position, Utils.defaultCharset);
                position = position + value.length;
            }
            this.put(field, value.data);

        }
    }


}
