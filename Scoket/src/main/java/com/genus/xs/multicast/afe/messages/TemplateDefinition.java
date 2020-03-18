package com.genus.xs.multicast.afe.messages;

import com.genus.xs.multicast.afe.TemplateLibrary;
import com.genus.xs.multicast.afe.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

/**
 * @author hfq
 * @date 2018/10/16
 */
public class TemplateDefinition extends Message {
    private static final Logger logger = LoggerFactory.getLogger(TemplateDefinition.class);

    public TemplateDefinition() {
        header.setMessageType(MessageType.TemplateDefinition);
    }


    @Override
    public void parse(byte[] bytes, int startPos) {
        if (header == null) {
            return;
        }
        long templateId = header.getItemNumber();
        List<Integer> template = new ArrayList<>();
        int position = header.getLength() + startPos;
        int fieldTotal = Utils.bytes2uint(bytes, 1, position);
        position = position + 1;
        StringBuilder sb = new StringBuilder();
        for (int fieldNo = 0; position < (header.getMessageSize() + startPos) && fieldNo < fieldTotal; position = position + 2) {
            int value = Utils.bytes2uint(bytes, 2, position);
            template.add(value);

            Field field = Field.FieldDefinition.resolve(value);
            if (field == null) {
                sb.append(" uu").append(value);
            } else {
                sb.append(" ").append(field.getName()).append("[").append(field.getType()).append("]");
            }
        }
        if (template.size() > 0) {
            TemplateLibrary.getInstance().addTemplate(templateId, template);
        }
    }


}
