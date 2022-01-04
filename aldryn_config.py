from aldryn_client import forms

class Form(forms.BaseForm):

    hide_related_services = forms.CheckboxField(
        "Hide Specific Services Selector",
        required=False,
        initial=False)
    summary_richtext = forms.CheckboxField(
        "Use rich text for Summary",
        required=False,
        initial=False)
    enable_pubdate = forms.CheckboxField(
        "Enable Published date",
        required=False,
        initial=False)
    enable_image = forms.CheckboxField(
        "Enable Featured image",
        required=False,
        initial=True)
    related_templates = forms.CharField(
        'Related services templates, comma separated', required=False
    )
    translate_is_published = forms.CheckboxField(
        'Translate Is published and Is featured fields', required=False, initial=False
    )
    translate_layout = forms.CheckboxField(
        'Translate layout field', required=False, initial=False
    )

    def to_settings(self, data, settings):

        settings['SERVICES_HIDE_RELATED_SERVICES'] = int(data['hide_related_services'])
        settings['SERVICES_SUMMARY_RICHTEXT'] = int(data['summary_richtext'])
        settings['SERVICES_ENABLE_PUBDATE'] = int(data['enable_pubdate'])
        settings['SERVICES_ENABLE_IMAGE'] = int(data['enable_image'])
        settings['SERVICES_TRANSLATE_IS_PUBLISHED'] = int(data['translate_is_published'])
        settings['SERVICES_TRANSLATE_LAYOUT'] = int(data['translate_layout'])
        if data['related_templates']:
            settings['SERVICES_RELATED_SERVICES_LAYOUTS'] = data['related_templates'].split(',')

        return settings
