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

    def to_settings(self, data, settings):

        if data['hide_related_services']:
            settings['SERVICES_HIDE_RELATED_SERVICES'] = int(data['hide_related_services'])
        if data['summary_richtext']:
            settings['SERVICES_SUMMARY_RICHTEXT'] = int(data['summary_richtext'])

        return settings
