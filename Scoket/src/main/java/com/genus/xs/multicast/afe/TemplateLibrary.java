package com.genus.xs.multicast.afe;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by Administrator on 2018/10/17.
 */
public class TemplateLibrary {

    private static TemplateLibrary instance = new TemplateLibrary();

    private TemplateLibrary() {

    }

    public static TemplateLibrary getInstance() {
        return instance;
    }

    private Map<Long, List<Integer>> library = new HashMap<>();

    public List<Integer> getTemplate(Long templateId) {
        return library.get(templateId);
    }

    public void addTemplate(Long templateId, List<Integer> templateList) {
        library.put(templateId, templateList);
    }

    public void clearAll() {
        library.clear();
    }

    public void remove(Long templateId) {
        library.remove(templateId);
    }

}
