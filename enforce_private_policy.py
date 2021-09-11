#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from mailman.interfaces.mailinglist import SubscriptionPolicy
from mailman.interfaces.action import Action
from mailman.model.mailinglist import ListArchiver, MailingList
from mailman.interfaces.mailinglist import ReplyToMunging
from mailman.interfaces.archiver import ArchivePolicy

from mailman.config import config
from sqlalchemy.orm import sessionmaker

def enforce(mailing, *args, **kw):
    """
    - big message size
    - increase max recipients
    - set replyto
    - make archives private
    - sanify archivers
    """
    mailing.subscription_policy = (
        SubscriptionPolicy.confirm_then_moderate)
    mailing.max_message_size = 2147483647
    mailing.max_num_recipients = 1000
    # mailing.default_nonmember_action = Action.discard
    mailing.reply_goes_to_list = ReplyToMunging.point_to_list
    mailing.first_strip_reply_to = True
    if mailing.archive_policy in [None, ArchivePolicy.public]:
        mailing.archive_policy = ArchivePolicy.private
    session = config.db.store
    to_delete = {}
    for i in session.query(ListArchiver).all():
        name = i.mailing_list.list_name
        mlist = to_delete.setdefault(name, {})
        archiver = mlist.setdefault(i.name, [])
        if i not in archiver:
            archiver.append(i)
    for mailinglist in [a for a in to_delete]:
        archivers = to_delete[mailinglist]
        for archivername in [a for a in archivers]:
            archiver = archivers[archivername]
            if len(archiver) > 1:
                print("fixing {0} archivers".format(mailinglist))
                for i in archiver[1:]:
                    session.delete(i)
    config.db.commit()


# vim:set et sts=4 ts=4 tw=80:
