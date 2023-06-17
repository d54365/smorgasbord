# -*- coding: utf-8 -*-

import logging

from dj_db_conn_pool.core.mixins import PooledDatabaseWrapperMixin
from sqlalchemy.dialects.mysql.pymysql import MySQLDialect_pymysql

from base.db.mysql import base

logger = logging.getLogger(__name__)


class DatabaseWrapper(PooledDatabaseWrapperMixin, base.DatabaseWrapper):
    # shardingsphere不支持函数Database()
    # 所以把introspection的get_table_list()改为了之前的版本

    class SQLAlchemyDialect(MySQLDialect_pymysql):
        pass

    def _set_dbapi_autocommit(self, autocommit):
        self.connection.connection.autocommit(autocommit)
