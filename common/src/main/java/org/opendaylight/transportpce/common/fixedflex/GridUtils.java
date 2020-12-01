/*
 * Copyright © 2020 Orange, Inc. and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */

package org.opendaylight.transportpce.common.fixedflex;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import org.opendaylight.yang.gen.v1.http.org.openroadm.common.optical.channel.types.rev200529.FrequencyGHz;
import org.opendaylight.yang.gen.v1.http.org.openroadm.common.optical.channel.types.rev200529.FrequencyTHz;
import org.opendaylight.yang.gen.v1.http.org.openroadm.network.types.rev200529.available.freq.map.AvailFreqMaps;
import org.opendaylight.yang.gen.v1.http.org.openroadm.network.types.rev200529.available.freq.map.AvailFreqMapsBuilder;
import org.opendaylight.yang.gen.v1.http.org.openroadm.network.types.rev200529.available.freq.map.AvailFreqMapsKey;
import org.opendaylight.yangtools.yang.common.Uint16;

/**
 * Util class for grid.
 *
 */
public final class GridUtils {

    private GridUtils() {
    }

    public static Map<AvailFreqMapsKey, AvailFreqMaps> initFreqMaps4FixedGrid2Available() {
        byte[] byteArray = new byte[GridConstant.NB_OCTECTS];
        Arrays.fill(byteArray, (byte) GridConstant.AVAILABLE_SLOT_VALUE);
        Map<AvailFreqMapsKey, AvailFreqMaps> waveMap = new HashMap<>();
        AvailFreqMaps availFreqMaps = new AvailFreqMapsBuilder().setMapName(GridConstant.C_BAND)
                .setFreqMapGranularity(new FrequencyGHz(BigDecimal.valueOf(GridConstant.GRANULARITY)))
                .setStartEdgeFreq(new FrequencyTHz(BigDecimal.valueOf(GridConstant.START_EDGE_FREQUENCY)))
                .setEffectiveBits(Uint16.valueOf(GridConstant.EFFECTIVE_BITS))
                .setFreqMap(byteArray)
                .build();
        waveMap.put(availFreqMaps.key(), availFreqMaps);
        return waveMap;
    }

    /**
     * Compute the wavelength index from Spectrum assignment stop index.
     * Only for fix grid and device 1.2.1.
     * @param stopIndex int
     * @return the wavelength number.
     */
    public static long getWaveLengthIndexFromSpectrumAssigment(int stopIndex) {
        return (stopIndex + 1) / GridConstant.NB_SLOTS_100G;
    }

    /**
     * Compute the frequency in TGz for the given index.
     * @param index int
     * @return the frequency in THz for the provided index.
     */
    public static BigDecimal getFrequencyFromIndex(int index) {
        int nvalue = index - 284;
        return BigDecimal.valueOf(GridConstant.CENTRAL_FREQUENCY + (nvalue * GridConstant.GRANULARITY / 1000));
    }

}
