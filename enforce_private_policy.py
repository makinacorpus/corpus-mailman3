#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from mailman.interfaces.mailinglist import SubscriptionPolicy
from mailman.interfaces.action import Action
from mailman.interfaces.mailinglist import ReplyToMunging
from mailman.interfaces.archiver import ArchivePolicy

from mailman.config import config  

def enforce(mailing):
    mailing.subscription_policy = (
        SubscriptionPolicy.confirm_then_moderate)
    mailing.max_message_size = 2147483647
    mailing.max_num_recipients = 1000
    mailing.default_nonmember_action = Action.discard
    mailing.reply_goes_to_list = ReplyToMunging.point_to_list
    mailing.first_strip_reply_to = True
    mailing.archive_policy = ArchivePolicy.private
    config.db.commit()


# vim:set et sts=4 ts=4 tw=80:
