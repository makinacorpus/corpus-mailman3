#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from mailman.interfaces.mailinglist import SubscriptionPolicy
from mailman.interfaces.action import Action
from mailman.interfaces.mailinglist import ReplyToMunging
from mailman.interfaces.archiver import ArchivePolicy
import sys
import os
from mailman.core.initialize import initialize

from mailman.config import config
SQL = '''
DO $$
    BEGIN
        IF to_regclass('makina_listarchiver_mailing_list_id_name_uniq') \
                    IS NULL THEN
            CREATE UNIQUE INDEX \
                makina_listarchiver_mailing_list_id_name_uniq \
                    ON listarchiver (mailing_list_id, name);
        END IF;
    END
$$;
'''


def main():
    cfg = os.environ.get('MAILMANCONFIG', 'mailman.cfg')
    initialize(cfg, True)
    config.db.engine.execute(SQL)
    config.db.commit()


if __name__ == '__main__':
    main()

# vim:set et sts=4 ts=4 tw=80:
