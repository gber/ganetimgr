# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# Copyright (C) 2010-2014 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from django import forms
from django.utils.translation import gettext_lazy
from django.contrib.auth.models import User
from notifications.models import NotificationArchive
from notifications.utils import get_mails


TYPE_CHOICES = (
    ('cluster', 'clusters'),
    ('nodes', 'nodes'),
    ('nodegroups', 'nodegroups'),
    ('users', 'users'),
    ('groups', 'groups'),
    ('instances', 'instances')
)


class MessageForm(forms.Form):
    search_for = forms.ChoiceField(
        label=gettext_lazy("Search for"),
        choices=TYPE_CHOICES
    )
    subject = forms.CharField(max_length=100, label=gettext_lazy("Subject"))
    message = forms.CharField(
        widget=forms.Textarea,
        label=gettext_lazy("Body"),
        help_text='You can use {% for i in instances %} {{ i }} {% endfor %} if you want to use the body as a mail template.'
    )
    recipient_list = forms.CharField(label=gettext_lazy("Recipients"))

    def add_to_archive(self, user):
        if self.is_valid():
            notification = NotificationArchive(
                subject=self.cleaned_data['subject'],
                message=self.cleaned_data['message'],
                sender=user
            )
            notification.save()
            mail_list = get_mails(self.cleaned_data['recipient_list'].split(','))
            for user in User.objects.filter(email__in=mail_list):
                notification.recipients.add(user)
            notification.save()
