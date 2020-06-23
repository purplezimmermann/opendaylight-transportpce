#!/usr/bin/env python

#############################################################################
# Copyright (c) 2017 Orange, Inc. and others.  All rights reserved.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#############################################################################

import unittest
import json
import time
#from unittest.result import failfast
import requests
from common import test_utils


class TransportPCERendererTesting(unittest.TestCase):

    processes = None

    @classmethod
    def setUpClass(cls):
        cls.processes = test_utils.start_tpce()
        cls.processes = test_utils.start_sims(['xpdra', 'roadma'])

    @classmethod
    def tearDownClass(cls):
        for process in cls.processes:
            test_utils.shutdown_process(process)
        print("all processes killed")

    def setUp(self):
        print("execution of {}".format(self.id().split(".")[-1]))
        time.sleep(10)

    def test_01_rdm_device_connected(self):
        response = test_utils.mount_device("ROADMA01", 'roadma')
        self.assertEqual(response.status_code, requests.codes.created, test_utils.CODE_SHOULD_BE_201)

    def test_02_xpdr_device_connected(self):
        response = test_utils.mount_device("XPDRA01", 'xpdra')
        self.assertEqual(response.status_code, requests.codes.created, test_utils.CODE_SHOULD_BE_201)

    def test_03_rdm_portmapping(self):
        url = ("{}/config/transportpce-portmapping:network/"
               "nodes/ROADMA01"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        self.assertIn(
            {'supporting-port': 'L1', 'supporting-circuit-pack-name': '2/0',
             'logical-connection-point': 'DEG1-TTP-TXRX', 'port-direction': 'bidirectional'},
            res['nodes'][0]['mapping'])
        self.assertIn(
            {'supporting-port': 'C7', 'supporting-circuit-pack-name': '4/0',
             'logical-connection-point': 'SRG1-PP7-TXRX', 'port-direction': 'bidirectional'},
            res['nodes'][0]['mapping'])

    def test_04_xpdr_portmapping(self):
        url = ("{}/config/transportpce-portmapping:network/"
               "nodes/XPDRA01"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        self.assertIn(
            {'supporting-port': '1', 'supporting-circuit-pack-name': '1/0/1-PLUG-NET',
             'logical-connection-point': 'XPDR1-NETWORK1', 'port-direction': 'bidirectional',
             'connection-map-lcp': 'XPDR1-CLIENT1', 'port-qual': 'xpdr-network',
             'lcp-hash-val': 'APdT8Jzj+EVC'},
            res['nodes'][0]['mapping'])
        self.assertIn(
            {'supporting-port': 'C1',
             'supporting-circuit-pack-name': '1/0/C1-PLUG-CLIENT',
             'logical-connection-point': 'XPDR1-CLIENT1', 'port-direction': 'bidirectional',
             'connection-map-lcp': 'XPDR1-NETWORK1', 'port-qual': 'xpdr-client',
             'lcp-hash-val': 'UHyVf5o4TF0='},
            res['nodes'][0]['mapping'])

    def test_05_service_path_create(self):
        url = "{}/operations/transportpce-device-renderer:service-path".format(test_utils.RESTCONF_BASE_URL)
        data = {"renderer:input": {
            "renderer:service-name": "service_test",
            "renderer:wave-number": "7",
            "renderer:modulation-format": "qpsk",
            "renderer:operation": "create",
            "renderer:nodes": [
                {"renderer:node-id": "ROADMA01",
                 "renderer:src-tp": "SRG1-PP7-TXRX",
                 "renderer:dest-tp": "DEG1-TTP-TXRX"},
                {"renderer:node-id": "XPDRA01",
                 "renderer:src-tp": "XPDR1-CLIENT1",
                 "renderer:dest-tp": "XPDR1-NETWORK1"}]}}
        response = requests.request(
            "POST", url, data=json.dumps(data),
            headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        self.assertIn('Roadm-connection successfully created for nodes: ROADMA01', res["output"]["result"])

    def test_06_service_path_create_rdm_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/ROADMA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/DEG1-TTP-TXRX-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        # the following statement replaces self.assertDictContainsSubset deprecated in python 3.2
        self.assertDictEqual(
            dict({
                'name': 'DEG1-TTP-TXRX-7',
                'administrative-state': 'inService',
                'supporting-circuit-pack-name': '2/0',
                'type': 'org-openroadm-interfaces:opticalChannel',
                'supporting-port': 'L1'
            }, **res['interface'][0]),
            res['interface'][0]
        )
        self.assertDictEqual(
            {'wavelength-number': 7},
            res['interface'][0]['org-openroadm-optical-channel-interfaces:och'])

    def test_07_service_path_create_rdm_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/ROADMA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/SRG1-PP7-TXRX-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        # the following statement replaces self.assertDictContainsSubset deprecated in python 3.2
        self.assertDictEqual(
            dict({
                'name': 'SRG1-PP7-TXRX-7',
                'administrative-state': 'inService',
                'supporting-circuit-pack-name': '4/0',
                'type': 'org-openroadm-interfaces:opticalChannel',
                'supporting-port': 'C7'
            }, **res['interface'][0]),
            res['interface'][0]
        )
        self.assertDictEqual(
            {'wavelength-number': 7},
            res['interface'][0]['org-openroadm-optical-channel-interfaces:och'])

    def test_08_service_path_create_rdm_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/ROADMA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "roadm-connections/SRG1-PP7-TXRX-DEG1-TTP-TXRX-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        # the following statement replaces self.assertDictContainsSubset deprecated in python 3.2
        self.assertDictEqual(
            dict({
                'connection-number': 'SRG1-PP7-TXRX-DEG1-TTP-TXRX-7',
                'wavelength-number': 7,
                'opticalControlMode': 'off'
            }, **res['roadm-connections'][0]),
            res['roadm-connections'][0]
        )
        self.assertDictEqual(
            {'src-if': 'SRG1-PP7-TXRX-7'},
            res['roadm-connections'][0]['source'])
        self.assertDictEqual(
            {'dst-if': 'DEG1-TTP-TXRX-7'},
            res['roadm-connections'][0]['destination'])

    def test_09_service_path_create_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-NETWORK1-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        # the following statement replaces self.assertDictContainsSubset deprecated in python 3.2
        self.assertDictEqual(
            dict({
                'name': 'XPDR1-NETWORK1-7',
                'administrative-state': 'inService',
                'supporting-circuit-pack-name': '1/0/1-PLUG-NET',
                'type': 'org-openroadm-interfaces:opticalChannel',
                'supporting-port': '1'
            }, **res['interface'][0]),
            res['interface'][0]
        )
        self.assertDictEqual(
            {u'rate': u'org-openroadm-optical-channel-interfaces:R100G',
             u'transmit-power': -5,
             u'wavelength-number': 7,
             u'modulation-format': u'dp-qpsk'},
            res['interface'][0]['org-openroadm-optical-channel-interfaces:och'])

    def test_10_service_path_create_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-NETWORK1-OTU"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        # the following statement replaces self.assertDictContainsSubset deprecated in python 3.2
        self.assertDictEqual(
            dict({
                'name': 'XPDR1-NETWORK1-OTU',
                'administrative-state': 'inService',
                'supporting-circuit-pack-name': '1/0/1-PLUG-NET',
                'type': 'org-openroadm-interfaces:otnOtu',
                'supporting-port': '1',
                'supporting-interface': 'XPDR1-NETWORK1-7'
            }, **res['interface'][0]),
            res['interface'][0]
        )
        self.assertDictEqual(
            {u'rate': u'org-openroadm-otn-otu-interfaces:OTU4',
             u'fec': u'scfec'},
            res['interface'][0]['org-openroadm-otn-otu-interfaces:otu'])

    def test_11_service_path_create_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-NETWORK1-ODU"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        # the 2 following statements replace self.assertDictContainsSubset deprecated in python 3.2
        self.assertDictEqual(
            dict({
                'name': 'XPDR1-NETWORK1-ODU',
                'administrative-state': 'inService',
                'supporting-circuit-pack-name': '1/0/1-PLUG-NET',
                'type': 'org-openroadm-interfaces:otnOdu',
                'supporting-port': '1',
                'supporting-interface': 'XPDR1-NETWORK1-OTU'
            }, **res['interface'][0]),
            res['interface'][0]
        )
        self.assertDictEqual(
            dict({
                'rate': 'org-openroadm-otn-odu-interfaces:ODU4',
                u'monitoring-mode': u'terminated'
            }, **res['interface'][0]['org-openroadm-otn-odu-interfaces:odu']),
            res['interface'][0]['org-openroadm-otn-odu-interfaces:odu']
        )
        self.assertDictEqual({u'exp-payload-type': u'07', u'payload-type': u'07'},
                             res['interface'][0]['org-openroadm-otn-odu-interfaces:odu']['opu'])

    def test_12_service_path_create_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-CLIENT1-ETHERNET"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        # the following statement replaces self.assertDictContainsSubset deprecated in python 3.2
        self.assertDictEqual(
            dict({
                'name': 'XPDR1-CLIENT1-ETHERNET',
                'administrative-state': 'inService',
                'supporting-circuit-pack-name': '1/0/C1-PLUG-CLIENT',
                'type': 'org-openroadm-interfaces:ethernetCsmacd',
                'supporting-port': 'C1'
            }, **res['interface'][0]),
            res['interface'][0]
        )
        self.assertDictEqual(
            {'speed': 100000,
             'mtu': 9000,
             'auto-negotiation': 'enabled',
             'duplex': 'full',
             'fec': 'off'},
            res['interface'][0]['org-openroadm-ethernet-interfaces:ethernet'])

    def test_13_service_path_create_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "circuit-packs/1%2F0%2F1-PLUG-NET"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        self.assertIn('not-reserved-inuse', res['circuit-packs'][0]["equipment-state"])

    def test_14_service_path_delete(self):
        url = "{}/operations/transportpce-device-renderer:service-path".format(test_utils.RESTCONF_BASE_URL)
        data = {"renderer:input": {
            "renderer:service-name": "service_test",
            "renderer:wave-number": "7",
            "renderer:operation": "delete",
            "renderer:nodes": [
                {"renderer:node-id": "ROADMA01",
                 "renderer:src-tp": "SRG1-PP7-TXRX",
                 "renderer:dest-tp": "DEG1-TTP-TXRX"},
                {"renderer:node-id": "XPDRA01",
                 "renderer:src-tp": "XPDR1-CLIENT1",
                 "renderer:dest-tp": "XPDR1-NETWORK1"}]}}
        response = requests.request(
            "POST", url, data=json.dumps(data),
            headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(response.json(), {
            'output': {'result': 'Request processed', 'success': True}})

    def test_15_service_path_delete_rdm_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/ROADMA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/DEG1-TTP-TXRX-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.not_found)
        res = response.json()
        self.assertIn(
            {"error-type": "application", "error-tag": "data-missing",
             "error-message": "Request could not be completed because the relevant data model content does not exist"},
            res['errors']['error'])

    def test_16_service_path_delete_rdm_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/ROADMA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/SRG1-PP7-TXRX-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.not_found)
        res = response.json()
        self.assertIn(
            {"error-type": "application", "error-tag": "data-missing",
                "error-message": "Request could not be completed because the relevant data model content does not exist"},
            res['errors']['error'])

    def test_17_service_path_delete_rdm_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/ROADMA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "roadm-connections/SRG1-PP7-TXRX-DEG1-TTP-TXRX-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.not_found)
        res = response.json()
        self.assertIn(
            {"error-type": "application", "error-tag": "data-missing",
                "error-message": "Request could not be completed because the relevant data model content does not exist"},
            res['errors']['error'])

    def test_18_service_path_delete_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-NETWORK1-7"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.not_found)
        res = response.json()
        self.assertIn(
            {"error-type": "application", "error-tag": "data-missing",
                "error-message": "Request could not be completed because the relevant data model content does not exist"},
            res['errors']['error'])

    def test_19_service_path_delete_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-NETWORK1-OTU"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.not_found)
        res = response.json()
        self.assertIn(
            {"error-type": "application", "error-tag": "data-missing",
                "error-message": "Request could not be completed because the relevant data model content does not exist"},
            res['errors']['error'])

    def test_20_service_path_delete_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-NETWORK1-ODU"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.not_found)
        res = response.json()
        self.assertIn(
            {"error-type": "application", "error-tag": "data-missing",
                "error-message": "Request could not be completed because the relevant data model content does not exist"},
            res['errors']['error'])

    def test_21_service_path_delete_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "interface/XPDR1-CLIENT1-ETHERNET"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.not_found)
        res = response.json()
        self.assertIn(
            {"error-type": "application", "error-tag": "data-missing",
                "error-message": "Request could not be completed because the relevant data model content does not exist"},
            res['errors']['error'])

    def test_22_service_path_delete_xpdr_check(self):
        url = ("{}/config/network-topology:network-topology/topology/topology-netconf/"
               "node/XPDRA01/yang-ext:mount/org-openroadm-device:org-openroadm-device/"
               "circuit-packs/1%2F0%2F1-PLUG-NET"
               .format(test_utils.RESTCONF_BASE_URL))
        response = requests.request(
            "GET", url, headers=test_utils.TYPE_APPLICATION_JSON, auth=(test_utils.ODL_LOGIN, test_utils.ODL_PWD))
        self.assertEqual(response.status_code, requests.codes.ok)
        res = response.json()
        self.assertEqual('not-reserved-available', res["circuit-packs"][0]['equipment-state'])

    def test_23_rdm_device_disconnected(self):
        response = test_utils.unmount_device("ROADMA01")
        self.assertEqual(response.status_code, requests.codes.ok, test_utils.CODE_SHOULD_BE_200)

    def test_24_xpdr_device_disconnected(self):
        response = test_utils.unmount_device("XPDRA01")
        self.assertEqual(response.status_code, requests.codes.ok, test_utils.CODE_SHOULD_BE_200)


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
