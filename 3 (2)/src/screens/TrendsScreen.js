import React, { useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  Dimensions, Modal, ActivityIndicator, StatusBar,
} from 'react-native';
import { Colors, Typography, S, R, Shadow } from '../theme';
import { useHealth, getOverallStatus } from '../context/HealthContext';
import { useTheme } from '../context/ThemeContext';
import { FullLineChart } from '../components/MiniChart';
import StatusBadge from '../components/StatusBadge';
import Card from '../components/Card';
import Icon from '../components/Icon';

const { width: SW } = Dimensions.get('window');
// scroll padding (xl*2=40) + card border (2) + card padding (lg*2=32) = 74
const CHART_W = Math.max(100, SW - 74);
const TABS    = [
  { label: 'Weight', icon: 'scale-outline' },
  { label: 'BP',     icon: 'heart-outline' },
  { label: 'Heart',  icon: 'pulse-outline' },
  { label: 'Steps',  icon: 'footsteps' },
  { label: 'Sleep',  icon: 'moon-outline' },
  { label: 'SpO₂',   icon: 'heart-circle-outline' },
];
const RANGES = ['7D', '30D', 'All'];
const rangeCounts = { '7D': 7, '30D': 30, 'All': 999 };

export default function TrendsScreen() {
  const { colors: c } = useTheme();
  const { records } = useHealth();
  const [tab, setTab]     = useState(0);
  const [range, setRange] = useState('7D');
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading]     = useState(false);
  const [done, setDone]           = useState(false);

  const sliced = [...records].slice(0, rangeCounts[range]).reverse();
  const labels = sliced.map(r => {
    const d = new Date(r.date);
    return `${d.getMonth()+1}/${d.getDate()}`;
  });

  const chartDataSets = [
    [{ data: sliced.map(r => r.weight    || 0), color: Colors.chart_teal, showArea: true  }],
    [
      { data: sliced.map(r => r.systolic  || 0), color: Colors.chart_sys,  showArea: false },
      { data: sliced.map(r => r.diastolic || 0), color: Colors.chart_dia,  showArea: false },
    ],
    [{ data: sliced.map(r => r.heartRate || 0), color: Colors.chart_hr,   showArea: true  }],
    [{ data: sliced.map(r => r.steps     || 0), color: '#10B981',          showArea: true  }],
    [{ data: sliced.map(r => r.sleep     || 0), color: '#6366F1',          showArea: true  }],
    [{ data: sliced.map(r => r.spO2      || 0), color: '#06B6D4',          showArea: true  }],
  ][tab];

  const chartProps = [
    { goalValue: 70 },
    { healthyBandMin: 60, healthyBandMax: 120 },
    { healthyBandMin: 60, healthyBandMax: 100 },
    { goalValue: 10000 },
    { healthyBandMin: 7, healthyBandMax: 9 },
    { healthyBandMin: 95, healthyBandMax: 100 },
  ][tab];

  const handleExport = () => {
    setShowModal(true); setLoading(true); setDone(false);
    setTimeout(() => { setLoading(false); setDone(true); }, 3000);
  };

  return (
    <View style={[s.root, { backgroundColor: c.bg }]}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />

      <View style={s.header}>
        <Text style={s.headerTitle}>Health Trends</Text>
        <TouchableOpacity style={s.exportBtn} onPress={handleExport}>
          <Icon name="document-text-outline" size={16} color={Colors.white} />
          <Text style={s.exportText}>Export PDF</Text>
        </TouchableOpacity>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={s.scroll}>

        {/* Metric Tabs — scrollable */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginHorizontal: -S.xl }}>
          <View style={[s.tabRow, { backgroundColor: c.card, marginHorizontal: S.xl }]}>
            {TABS.map((t, i) => (
              <TouchableOpacity
                key={t.label}
                onPress={() => setTab(i)}
                style={[s.tabBtn, tab === i && s.tabBtnActive]}
              >
                <Icon name={t.icon} size={14} color={tab === i ? Colors.primary : c.text3} />
                <Text style={[s.tabText, { color: tab === i ? Colors.primary : c.text3 }, tab === i && s.tabTextActive]}>{t.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>

        {/* Range Picker */}
        <View style={s.rangeRow}>
          {RANGES.map(r => (
            <TouchableOpacity
              key={r} onPress={() => setRange(r)}
              style={[s.rangeBtn, { backgroundColor: c.card, borderColor: c.border }, range === r && s.rangeBtnActive]}
            >
              <Text style={[s.rangeBtnText, { color: c.text2 }, range === r && s.rangeBtnTextActive]}>{r}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Chart */}
        <Card>
          {[
            <View style={s.legend}>
              <View style={s.legendItem}><View style={[s.legendDot, { backgroundColor: Colors.chart_teal }]} /><Text style={[s.legendText, { color: c.text3 }]}>Weight</Text></View>
              <View style={s.legendItem}><View style={s.legendDash} /><Text style={[s.legendText, { color: c.text3 }]}>Goal: 70 kg</Text></View>
            </View>,
            <View style={s.legend}>
              <View style={s.legendItem}><View style={[s.legendDot, { backgroundColor: Colors.chart_sys }]} /><Text style={[s.legendText, { color: c.text3 }]}>Systolic</Text></View>
              <View style={s.legendItem}><View style={[s.legendDot, { backgroundColor: Colors.chart_dia }]} /><Text style={[s.legendText, { color: c.text3 }]}>Diastolic</Text></View>
              <View style={s.legendItem}><View style={s.legendBand} /><Text style={[s.legendText, { color: c.text3 }]}>Normal range</Text></View>
            </View>,
            <View style={s.legend}>
              <View style={s.legendItem}><View style={[s.legendDot, { backgroundColor: Colors.chart_hr }]} /><Text style={[s.legendText, { color: c.text3 }]}>Heart Rate</Text></View>
              <View style={s.legendItem}><View style={s.legendBand} /><Text style={[s.legendText, { color: c.text3 }]}>60–100 bpm</Text></View>
            </View>,
            <View style={s.legend}>
              <View style={s.legendItem}><View style={[s.legendDot, { backgroundColor: '#10B981' }]} /><Text style={[s.legendText, { color: c.text3 }]}>Daily Steps</Text></View>
              <View style={s.legendItem}><View style={s.legendDash} /><Text style={[s.legendText, { color: c.text3 }]}>Goal: 10,000</Text></View>
            </View>,
            <View style={s.legend}>
              <View style={s.legendItem}><View style={[s.legendDot, { backgroundColor: '#6366F1' }]} /><Text style={[s.legendText, { color: c.text3 }]}>Sleep (hrs)</Text></View>
              <View style={s.legendItem}><View style={s.legendBand} /><Text style={[s.legendText, { color: c.text3 }]}>7–9 hrs optimal</Text></View>
            </View>,
            <View style={s.legend}>
              <View style={s.legendItem}><View style={[s.legendDot, { backgroundColor: '#06B6D4' }]} /><Text style={[s.legendText, { color: c.text3 }]}>Blood Oxygen</Text></View>
              <View style={s.legendItem}><View style={s.legendBand} /><Text style={[s.legendText, { color: c.text3 }]}>≥95% normal</Text></View>
            </View>,
          ][tab]}
          <FullLineChart
            dataSets={chartDataSets}
            labels={labels}
            width={CHART_W}
            height={200}
            {...chartProps}
          />
        </Card>

        {/* Stats row */}
        <View style={s.statsRow}>
          {[
            [
              { label: 'Avg Weight', value: `${(sliced.reduce((a,r)=>a+(r.weight||0),0)/sliced.length).toFixed(1)} kg`, icon: 'scale-outline' },
              { label: 'Min',        value: `${Math.min(...sliced.map(r=>r.weight||0)).toFixed(1)} kg`, icon: 'arrow-down-outline' },
              { label: 'Max',        value: `${Math.max(...sliced.map(r=>r.weight||0)).toFixed(1)} kg`, icon: 'arrow-up-outline' },
            ],
            [
              { label: 'Avg Systolic',  value: `${Math.round(sliced.reduce((a,r)=>a+(r.systolic||0),0)/sliced.length)} mmHg`, icon: 'heart-outline' },
              { label: 'Avg Diastolic', value: `${Math.round(sliced.reduce((a,r)=>a+(r.diastolic||0),0)/sliced.length)} mmHg`, icon: 'heart-outline' },
              { label: 'Avg HR',        value: `${Math.round(sliced.reduce((a,r)=>a+(r.heartRate||0),0)/sliced.length)} bpm`,  icon: 'pulse-outline' },
            ],
            [
              { label: 'Avg HR',  value: `${Math.round(sliced.reduce((a,r)=>a+(r.heartRate||0),0)/sliced.length)} bpm`, icon: 'pulse-outline' },
              { label: 'Min HR',  value: `${Math.min(...sliced.map(r=>r.heartRate||0))} bpm`, icon: 'arrow-down-outline' },
              { label: 'Max HR',  value: `${Math.max(...sliced.map(r=>r.heartRate||0))} bpm`, icon: 'arrow-up-outline' },
            ],
            [
              { label: 'Avg Steps', value: `${Math.round(sliced.reduce((a,r)=>a+(r.steps||0),0)/sliced.length).toLocaleString()}`, icon: 'footsteps' },
              { label: 'Best Day',  value: `${Math.max(...sliced.map(r=>r.steps||0)).toLocaleString()}`,  icon: 'trophy-outline' },
              { label: 'Goal Hit',  value: `${sliced.filter(r=>(r.steps||0)>=10000).length}/${sliced.length}d`, icon: 'checkmark-circle-outline' },
            ],
            [
              { label: 'Avg Sleep', value: `${(sliced.reduce((a,r)=>a+(r.sleep||0),0)/sliced.length).toFixed(1)} h`, icon: 'moon-outline' },
              { label: 'Best Night',value: `${Math.max(...sliced.map(r=>r.sleep||0)).toFixed(1)} h`, icon: 'arrow-up-outline' },
              { label: '7h+ Nights',value: `${sliced.filter(r=>(r.sleep||0)>=7).length}/${sliced.length}d`, icon: 'checkmark-circle-outline' },
            ],
            [
              { label: 'Avg SpO₂', value: `${(sliced.reduce((a,r)=>a+(r.spO2||0),0)/sliced.length).toFixed(1)}%`, icon: 'heart-circle-outline' },
              { label: 'Min',       value: `${Math.min(...sliced.map(r=>r.spO2||0))}%`, icon: 'arrow-down-outline' },
              { label: 'Max',       value: `${Math.max(...sliced.map(r=>r.spO2||0))}%`, icon: 'arrow-up-outline' },
            ],
          ][tab].map(st => (
            <Card key={st.label} style={s.miniStat}>
              <Icon name={st.icon} size={16} color={Colors.primary} style={{ marginBottom: 6 }} />
              <Text style={[s.miniStatVal, { color: c.text1 }]}>{st.value}</Text>
              <Text style={[s.miniStatLabel, { color: c.text3 }]}>{st.label}</Text>
            </Card>
          ))}
        </View>

        {/* Data Table */}
        <Card pad={false}>
          <View style={[s.tableHead, { backgroundColor: c.border_light, borderBottomColor: c.border }]}>
            <Text style={[s.thCell, { flex: 1.2, color: c.text2 }]}>Date</Text>
            <Text style={[s.thCell, { color: c.text2 }]}>Weight</Text>
            <Text style={[s.thCell, { color: c.text2 }]}>BP</Text>
            <Text style={[s.thCell, { color: c.text2 }]}>HR</Text>
            <Text style={[s.thCell, { color: c.text2 }]}>Status</Text>
          </View>
          {[...sliced].reverse().map((r, i) => (
            <View key={r.id} style={[s.tableRow, i % 2 === 0 && { backgroundColor: c.border_light + '50' }]}>
              <Text style={[s.tdCell, { flex: 1.2, fontWeight: '600', color: c.text1 }]}>
                {new Date(r.date).toLocaleDateString('en-US',{month:'short',day:'numeric'})}
              </Text>
              <Text style={[s.tdCell, { color: c.text1 }]}>{r.weight}</Text>
              <Text style={[s.tdCell, { color: c.text1 }]}>{r.systolic}/{r.diastolic}</Text>
              <Text style={[s.tdCell, { color: c.text1 }]}>{r.heartRate}</Text>
              <View style={{ flex: 1 }}><StatusBadge status={getOverallStatus(r)} /></View>
            </View>
          ))}
        </Card>

        <View style={{ height: 110 }} />
      </ScrollView>

      {/* Export Modal */}
      <Modal visible={showModal} transparent animationType="fade">
        <View style={[s.overlay, { backgroundColor: c.overlay }]}>
          <View style={[s.modal, { backgroundColor: c.card }]}>
            {loading ? (
              <View style={s.modalLoading}>
                <ActivityIndicator size="large" color={Colors.primary} />
                <Text style={[s.modalTitle, { color: c.text1 }]}>Generating report…</Text>
                <Text style={[s.modalSub, { color: c.text2 }]}>Building your health summary</Text>
              </View>
            ) : (
              <View style={s.modalDone}>
                <View style={s.modalCheckWrap}>
                  <Icon name="checkmark-circle" size={52} color={Colors.accent} />
                </View>
                <Text style={[s.modalTitle, { color: c.text1 }]}>Report Ready</Text>

                <View style={[s.pdfCard, { backgroundColor: c.bg, borderColor: c.border }]}>
                  <View style={s.pdfHeader}>
                    <Icon name="heart" size={16} color={Colors.primary} />
                    <Text style={s.pdfBrand}>  Health Monitor Report</Text>
                  </View>
                  <Text style={[s.pdfDate, { color: c.text3 }]}>
                    Generated {new Date().toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'})}
                  </Text>
                  <View style={[s.pdfDivider, { backgroundColor: c.border }]} />
                  <View style={s.pdfStats}>
                    {[
                      { l: 'Avg Weight', v: '72.5 kg' },
                      { l: 'Avg BP',     v: '118/76'  },
                      { l: 'Avg HR',     v: '72 bpm'  },
                    ].map(st => (
                      <View key={st.l} style={s.pdfStat}>
                        <Text style={[s.pdfStatVal, { color: c.text1 }]}>{st.v}</Text>
                        <Text style={[s.pdfStatLabel, { color: c.text3 }]}>{st.l}</Text>
                      </View>
                    ))}
                  </View>
                  <View style={s.pdfNote}>
                    <Icon name="checkmark-circle" size={13} color={Colors.accent} />
                    <Text style={s.pdfNoteText}>  All vitals within normal range</Text>
                  </View>
                </View>

                <TouchableOpacity style={s.downloadBtn} onPress={() => { setShowModal(false); setDone(false); }}>
                  <Icon name="download-outline" size={18} color={Colors.white} />
                  <Text style={s.downloadText}>  Download PDF</Text>
                </TouchableOpacity>
                <TouchableOpacity style={s.closeBtn} onPress={() => { setShowModal(false); setDone(false); }}>
                  <Text style={[s.closeBtnText, { color: c.text3 }]}>Close</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1 },
  header: {
    backgroundColor: Colors.primary,
    paddingTop: 52, paddingBottom: 16, paddingHorizontal: S.xl,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
  },
  headerTitle: { ...Typography.h2, color: Colors.white },
  exportBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: 'rgba(255,255,255,0.12)',
    borderRadius: R.md, paddingHorizontal: 14, paddingVertical: 9,
  },
  exportText: { ...Typography.bodySm, color: Colors.white, fontWeight: '600' },

  scroll: { padding: S.xl, gap: 14 },

  tabRow: {
    flexDirection: 'row', gap: 8,
    borderRadius: R.xl, padding: 6, ...Shadow.xs,
  },
  tabBtn: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 5, paddingVertical: 9, borderRadius: R.lg,
  },
  tabBtnActive: { backgroundColor: Colors.primary + '12' },
  tabText:      { ...Typography.label, textTransform: 'none', fontWeight: '500', letterSpacing: 0 },
  tabTextActive:{ fontWeight: '700' },

  rangeRow: { flexDirection: 'row', gap: 8 },
  rangeBtn: {
    flex: 1, alignItems: 'center', paddingVertical: 9,
    borderRadius: R.lg, borderWidth: 1, ...Shadow.xs,
  },
  rangeBtnActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  rangeBtnText:   { ...Typography.bodySm, fontWeight: '600' },
  rangeBtnTextActive: { color: Colors.white },

  legend:      { flexDirection: 'row', gap: 16, marginBottom: 12 },
  legendItem:  { flexDirection: 'row', alignItems: 'center', gap: 6 },
  legendDot:   { width: 10, height: 10, borderRadius: 5 },
  legendBand:  { width: 16, height: 8, borderRadius: 2, backgroundColor: Colors.healthy_fill, borderWidth: 1, borderColor: Colors.accent + '40' },
  legendDash:  { width: 16, height: 2, borderRadius: 1, backgroundColor: Colors.accent },
  legendText:  { ...Typography.label, textTransform: 'none', fontWeight: '500', letterSpacing: 0 },

  statsRow:    { flexDirection: 'row', gap: 10 },
  miniStat:    { flex: 1, alignItems: 'flex-start' },
  miniStatVal: { ...Typography.monoXs, fontWeight: '700', marginBottom: 2 },
  miniStatLabel:{ ...Typography.label, textTransform: 'none', fontWeight: '400', letterSpacing: 0 },

  tableHead: {
    flexDirection: 'row', paddingHorizontal: S.lg, paddingVertical: 10,
    borderBottomWidth: 1.5,
    borderTopLeftRadius: R.xl, borderTopRightRadius: R.xl,
  },
  thCell:    { flex: 1, ...Typography.label, textTransform: 'uppercase' },
  tableRow:  { flexDirection: 'row', paddingHorizontal: S.lg, paddingVertical: 11, alignItems: 'center' },
  tdCell:    { flex: 1, ...Typography.bodySm },

  overlay:   { flex: 1, alignItems: 'center', justifyContent: 'center', padding: S.xl },
  modal:     { borderRadius: R.xxl, width: '100%', overflow: 'hidden', ...Shadow.lg },
  modalLoading: { alignItems: 'center', padding: S.xxl, gap: 12 },
  modalDone:    { padding: S.xxl, alignItems: 'center', gap: 10 },
  modalCheckWrap:{ marginBottom: 4 },
  modalTitle:   { ...Typography.h3 },
  modalSub:     { ...Typography.bodySm },

  pdfCard: {
    width: '100%', borderRadius: R.lg, padding: S.lg,
    borderWidth: 1, marginVertical: 4,
  },
  pdfHeader:    { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  pdfBrand:     { ...Typography.bodySm, fontWeight: '700', color: Colors.primary },
  pdfDate:      { ...Typography.label, textTransform: 'none', fontWeight: '400', letterSpacing: 0, marginBottom: 10 },
  pdfDivider:   { height: 1, marginBottom: 10 },
  pdfStats:     { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 10 },
  pdfStat:      { alignItems: 'center', gap: 2 },
  pdfStatVal:   { ...Typography.monoXs, fontWeight: '700' },
  pdfStatLabel: { ...Typography.label, textTransform: 'none', fontWeight: '400', letterSpacing: 0 },
  pdfNote:      { flexDirection: 'row', alignItems: 'center' },
  pdfNoteText:  { ...Typography.label, color: Colors.accent, textTransform: 'none', fontWeight: '600', letterSpacing: 0 },

  downloadBtn: {
    width: '100%', flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    backgroundColor: Colors.primary, borderRadius: R.md, paddingVertical: 14, ...Shadow.md,
  },
  downloadText: { ...Typography.h4, color: Colors.white },
  closeBtn:     { paddingVertical: 8 },
  closeBtnText: { ...Typography.bodySm },
});
