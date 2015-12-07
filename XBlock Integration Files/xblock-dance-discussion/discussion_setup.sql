CREATE TABLE IF NOT EXISTS discussion.discussion_table (
comment_id int(11) NOT NULL AUTO_INCREMENT,
thread_id int(11) NOT NULL DEFAULT -1,
user_id varchar(254) COLLATE utf8_bin DEFAULT NULL,
user_name varchar(254) COLLATE utf8_bin DEFAULT NULL,
comment varchar(1024) COLLATE utf8_bin DEFAULT NULL,
parent_id int(11) DEFAULT -1,
creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY(comment_id)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;