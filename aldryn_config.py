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

    def to_settings(self, data, settings):

        if data['hide_related_services']:
            settings['SERVICES_HIDE_RELATED_SERVICES'] = int(data['hide_related_services'])
        if data['summary_richtext']:
            settings['SERVICES_SUMMARY_RICHTEXT'] = int(data['summary_richtext'])
        if data['enable_pubdate']:
            settings['SERVICES_ENABLE_PUBDATE'] = int(data['enable_pubdate'])
        if data['enable_image']:
            settings['SERVICES_ENABLE_IMAGE'] = int(data['enable_image'])

        return settings
