-- Initialize the Weight Management Database

-- Create and select the database
CREATE DATABASE IF NOT EXISTS `weight`;
USE weight;

-- Create containers_registered table
-- Stores information about registered containers and their weights
CREATE TABLE IF NOT EXISTS `containers_registered` (
  `container_id` varchar(15) NOT NULL,       -- Unique container identifier
  `weight` int(12) DEFAULT NULL,            -- Container's weight
  `unit` varchar(10) DEFAULT NULL,          -- Weight unit (e.g., kg)
  PRIMARY KEY (`container_id`)              -- Set container_id as primary key
) ENGINE=MyISAM;

-- Create transactions table
-- Records all weighing transactions including truck and container details
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` int(12) NOT NULL AUTO_INCREMENT,     -- Unique transaction identifier
  `datetime` datetime DEFAULT NULL,         -- Date and time of transaction
  `direction` varchar(10) DEFAULT NULL,     -- Direction (in/out)
  `truck` varchar(50) DEFAULT NULL,         -- Truck identifier
  `containers` varchar(10000) DEFAULT NULL, -- List of containers on truck
  `bruto` int(12) DEFAULT NULL,            -- Gross weight
  `truckTara` int(12) DEFAULT NULL,        -- Truck's empty weight
  `neto` int(12) DEFAULT NULL,             -- Net weight (bruto - tara)
  `produce` varchar(50) DEFAULT NULL,       -- Type of produce being transported
  PRIMARY KEY (`id`)                        -- Set id as primary key
) ENGINE=MyISAM AUTO_INCREMENT=10001;

-- End of initialization script