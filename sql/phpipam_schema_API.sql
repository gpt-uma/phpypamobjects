--
-- Additional custom fields in table `ipaddresses` supporting high level API and scan agent
--
LOCK TABLES `ipaddresses` WRITE;

ALTER TABLE `ipaddresses` ADD COLUMN (
  `custom_apiblock` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Client API does not allow update or deletion of this address',
  `custom_apinotremovable` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Client API does not allow deletion of this address',
  `custom_tcpports` varchar(150) DEFAULT NULL COMMENT 'List of detected open ports',

  `custom_scanagentid` int NOT NULL DEFAULT '0' COMMENT 'Id of agent that added this address',
  `custom_scanfirstdate` datetime DEFAULT NULL COMMENT 'Date of creation by agent',
  `custom_OS_current` varchar(1)  DEFAULT NULL COMMENT 'Current OS (W:Windows | U:Linux/UNIX)',
  `custom_OS_detected` varchar(100) DEFAULT NULL COMMENT 'Operating System detected by scan agent'
);

UNLOCK TABLES;

--
-- Additional tags for annotate_subnet() function.
--


LOCK TABLES `ipTags` WRITE;

INSERT INTO `ipTags` VALUES
    (5,'DHCP static',1,'#0f00ff','#ffffff','No','No',0),
    (6,'Static IP',1,'#ffa300','#000000','No','No',0),
    (7,'Router',1,'#00ffcc','#000000','No','No',0),
    (8,'Unusable',1,'#888888','#ffffff','No','No',0)
    ;

UNLOCK TABLES;
