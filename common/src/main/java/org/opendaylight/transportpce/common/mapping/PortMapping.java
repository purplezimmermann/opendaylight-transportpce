/*
 * Copyright © 2017 AT&T and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */

package org.opendaylight.transportpce.common.mapping;

import org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.portmapping.rev170228.network.nodes.Mapping;

public interface PortMapping {

    /**
     * This method creates logical to physical port mapping for a given device.
     * Instead of parsing all the circuit packs/ports in the device this methods
     * does a selective read operation on degree/srg subtree to get circuit
     * packs/ports that map to :
     *
     * <p>
     * 1. DEGn-TTP-TX, DEGn-TTP-RX, DEGn-TTP-TXRX
     *
     * <p>
     * 2. SRGn-PPp-TX, SRGn-PPp-RX, SRGn-PPp-TXRX
     *
     * <p>
     * 3. LINEn
     *
     * <p>
     * 4. CLNTn.
     *
     * <p>
     * If the port is Mw it also store the OMS, OTS interface provisioned on the
     * port. It skips the logical ports that are internal. If operation is
     * successful the mapping gets stored in datastore corresponding to
     * portmapping.yang data model.
     *
     * @return true/false based on status of operation
     */
    boolean createMappingData(String nodeId);

    /**
     * This method for a given node's termination point returns the Mapping object based on
     * portmapping.yang model stored in the MD-SAL data store which is created when the node is
     * connected for the first time. The mapping object basically contains the following attributes of
     * interest:
     *
     * <p>
     * 1. Supporting circuit pack
     *
     * <p>
     * 2. Supporting port
     *
     * <p>
     * 3. Supporting OMS interface (if port on ROADM) 4. Supporting OTS interface (if port on ROADM)
     *
     * @param nodeId Unique Identifier for the node of interest.
     * @param logicalConnPoint Name of the logical point
     *
     * @return Result Mapping object if success otherwise null.
     */

    Mapping getMapping(String nodeId, String logicalConnPoint);
}
