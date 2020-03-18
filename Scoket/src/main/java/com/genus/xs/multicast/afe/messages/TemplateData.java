package com.genus.xs.multicast.afe.messages;

import com.genus.xs.multicast.afe.TemplateLibrary;
import com.genus.xs.multicast.afe.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

/**
 * @author hfq
 * @date 2018/10/16
 */
public class TemplateData extends Message {
    private static final Logger logger = LoggerFactory.getLogger(TemplateData.class);

    public TemplateData() {
        header.setMessageType(MessageType.TemplateData);
    }

    @Override
    public void parse(byte[] bytes, int startPos) {
        if (header == null) {
            return;
        }
        int position = header.getLength() + startPos;
        long templateId = header.getItemNumber();
        List<Integer> template = TemplateLibrary.getInstance().getTemplate(templateId);
        if (template != null) {
            for (Integer t : template) {
                if (position >= bytes.length) {
                    break;
                }
                Field field = Field.FieldDefinition.resolve(t);
                DataType.DataTypeWrapper value;
                if (field != null) {
                    value = (DataType.DataTypeWrapper) field.parse(bytes, position, Utils.defaultCharset);

                } else {
                    DataType dataType = Utils.getFieldType(t);
                    value = dataType.parse(bytes, position, Utils.defaultCharset);
                }
                position = position + value.length;
                this.put(field, value.data);
            }
        } else {
//            logger.info("template is null {}",templateId);
        }

    }


}
