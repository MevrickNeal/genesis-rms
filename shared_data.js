// shared_data.js - Universal Real-Time SCADA Telemetry Engine for Genesis RMS
const TOTAL_UNITS_COUNT = 492; // 492 units across 8 divisions

const DIVISIONS_DIST = [
  { name: 'Dhaka', count: 208, center: [23.8103, 90.4125], rLng: [89.8, 90.9], rLat: [23.2, 24.4] },
  { name: 'Chittagong', count: 118, center: [22.3569, 91.7832], rLng: [91.3, 92.4], rLat: [21.4, 23.2] },
  { name: 'Sylhet', count: 58, center: [24.8949, 91.8687], rLng: [91.3, 92.5], rLat: [24.1, 25.2] },
  { name: 'Rajshahi', count: 38, center: [24.3636, 88.6241], rLng: [88.1, 89.4], rLat: [24.0, 25.1] },
  { name: 'Khulna', count: 30, center: [22.8456, 89.5403], rLng: [89.0, 89.9], rLat: [21.8, 23.4] },
  { name: 'Barisal', count: 15, center: [22.7010, 90.3535], rLng: [90.0, 90.8], rLat: [21.9, 23.1] },
  { name: 'Rangpur', count: 15, center: [25.7439, 89.2752], rLng: [88.4, 89.6], rLat: [25.3, 26.3] },
  { name: 'Mymensingh', count: 10, center: [24.7471, 90.4203], rLng: [89.8, 90.8], rLat: [24.5, 25.2] }
];

const OPERATORS = ['Grameenphone', 'Robi Axiata', 'Banglalink', 'Teletalk'];
const MODELS = ['Perkins 1104A-44TG2', 'Perkins 1104C-44TAG2', 'Perkins 1106A-70TAG2', 'Perkins 1103A-33G'];
const CAPACITIES = ['60 kVA / 48 kW Prime', '30 kVA / 24 kW Standby', '100 kVA / 80 kW Prime', '150 kVA / 120 kW Prime'];

const DISTRICTS = {
  Dhaka: ['Dhaka North (Mirpur)', 'Dhaka South (Gulshan)', 'Gazipur', 'Narayanganj', 'Tangail'],
  Chittagong: ['Chittagong Port', 'Cox\'s Bazar', 'Comilla', 'Feni', 'Rangamati'],
  Sylhet: ['Sylhet Sadar', 'Moulvibazar', 'Habiganj', 'Sunamganj'],
  Rajshahi: ['Rajshahi City', 'Bogra', 'Pabna', 'Naogaon'],
  Khulna: ['Khulna Metro', 'Jessore', 'Kushtia', 'Satkhira'],
  Barisal: ['Barisal Sadar', 'Patuakhali', 'Bhola', 'Pirojpur'],
  Rangpur: ['Rangpur City', 'Dinajpur', 'Kurigram', 'Gaibandha'],
  Mymensingh: ['Mymensingh Town', 'Jamalpur', 'Netrokona', 'Sherpur']
};

let GENERATORS = [];
let unitIndex = 1;

DIVISIONS_DIST.forEach(div => {
  for (let i = 0; i < div.count; i++) {
    const op = OPERATORS[(unitIndex - 1) % OPERATORS.length];
    const opCode = op === 'Grameenphone' ? 'GP' : op === 'Robi Axiata' ? 'RO' : op === 'Banglalink' ? 'BA' : 'TE';
    const model = MODELS[(unitIndex - 1) % MODELS.length];
    const capacity = CAPACITIES[(unitIndex - 1) % CAPACITIES.length];
    const dList = DISTRICTS[div.name];
    const district = dList[i % dList.length];

    let status = 'RUNNING';
    if (unitIndex <= 6) status = 'CRITICAL';
    else if (unitIndex <= 20) status = 'WARNING';
    else if (unitIndex > 452) status = 'STANDBY';

    let kw = status === 'STANDBY' ? 0.0 : (16.0 + ((unitIndex * 7) % 32) + Math.random() * 0.8).toFixed(1);
    let rpm = status === 'STANDBY' ? 0 : 1500;
    let temp = status === 'STANDBY' ? 28.0 : status === 'CRITICAL' ? (98.0 + (unitIndex % 12)).toFixed(1) : (82.0 + (unitIndex % 8)).toFixed(1);
    let fuel = Math.max(12, 95 - ((unitIndex * 3) % 75));
    let oil = status === 'STANDBY' ? 0.0 : (4.0 + ((unitIndex % 5) * 0.1)).toFixed(1);

    const lat = div.rLat[0] + Math.random() * (div.rLat[1] - div.rLat[0]);
    const lng = div.rLng[0] + Math.random() * (div.rLng[1] - div.rLng[0]);

    GENERATORS.push({
      id: `GEN-PK-${String(unitIndex).padStart(4, '0')}`,
      uid: `PK-1104-${String(unitIndex).padStart(4, '0')}`,
      station: `Tower BTS-${opCode}-${String(unitIndex).padStart(4, '0')}`,
      operator: op,
      area: div.name,
      district: district,
      model: model,
      capacity: capacity,
      status: status,
      kw: parseFloat(kw),
      load_pct: status === 'STANDBY' ? 0 : Math.round((kw / 48) * 100),
      rpm: rpm,
      temp: parseFloat(temp),
      fuel: fuel,
      oil: parseFloat(oil),
      runtime: (300 + (unitIndex * 19) % 1800),
      lat: parseFloat(lat.toFixed(4)),
      lng: parseFloat(lng.toFixed(4)),
      // 18 Data Points (DSE-7320 register map)
      p1_v1n: 230.4, p2_v2n: 229.8, p3_v3n: 230.1,
      p4_v12: 399.8, p5_v23: 400.2, p6_v31: 400.0,
      p7_i1: 27.2, p8_i2: 26.8, p9_i3: 27.0,
      p10_freq: 50.02, p11_kw: 18.6, p12_kva: 23.25,
      p13_kvar: 13.95, p14_pf: '0.80',
      p15_rpm: 1500, p16_temp: 84.2, p17_oil: 4.2,
      p18_fuel_liters: 190
    });

    unitIndex++;
  }
});

// Primary node is unit 104 (BTS-GP-0492)
const primaryNode = GENERATORS[103] || GENERATORS[0];
primaryNode.id = 'GEN-PK-0104';
primaryNode.uid = 'PK-1104-0104';
primaryNode.station = 'Tower BTS-GP-0492';
primaryNode.operator = 'Grameenphone';
primaryNode.area = 'Dhaka';
primaryNode.district = 'Dhaka North (Mirpur)';
primaryNode.model = 'Perkins 1104A-44TG2';
primaryNode.status = 'RUNNING';
primaryNode.fuel = 76;
primaryNode.p18_fuel_liters = 190;

function describeArc(cx, cy, r, startAngle, endAngle) {
  const startRad = (startAngle * Math.PI) / 180;
  const endRad = (endAngle * Math.PI) / 180;
  const x1 = cx + r * Math.cos(startRad);
  const y1 = cy + r * Math.sin(startRad);
  const x2 = cx + r * Math.cos(endRad);
  const y2 = cy + r * Math.sin(endRad);
  const largeArcFlag = ((endAngle - startAngle) % 360 + 360) % 360 > 180 ? 1 : 0;
  return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r.toFixed(2)} ${r.toFixed(2)} 0 ${largeArcFlag} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`;
}

// 6-Month Daily Telemetry Data (180 days: June 1 - Nov 15, 2026)
let HISTORY_180_DAYS = [];
const startDate = new Date(2026, 5, 1);
for (let d = 0; d < 180; d++) {
  const curr = new Date(startDate.getTime() + d * 86400000);
  const iso = curr.toISOString().split('T')[0];
  const seasonal = Math.sin((d / 180) * Math.PI);
  const dailyKwh = Math.round(1120 + seasonal * 320 + (d % 7) * 22 + Math.random() * 45);
  const voltage = +(398.8 + Math.sin(d) * 1.6 + Math.random() * 0.5).toFixed(1);
  const fuelLiters = +(240 + seasonal * 70 + (dailyKwh / 100) * 3 + Math.random() * 8).toFixed(1);
  const loadFactor = Math.min(94, Math.round(62 + seasonal * 24 + Math.random() * 6));
  HISTORY_180_DAYS.push({ date: iso, kwh: dailyKwh, voltage: voltage, fuel: fuelLiters, loadFactor: loadFactor });
}

// Real-Time Machine Activation / Deactivation toggle
function toggleMachineStatus(genId, isActive) {
  const g = GENERATORS.find(u => u.id === genId);
  if (!g) return;
  if (isActive) {
    g.status = 'RUNNING';
    g.kw = +(16.0 + ((Math.random() * 15))).toFixed(1);
    g.load_pct = Math.round((g.kw / 48) * 100);
    g.rpm = 1500;
    g.oil = 4.2;
    g.p11_kw = g.kw;
    g.p15_rpm = 1500;
  } else {
    g.status = 'STANDBY';
    g.kw = 0.0;
    g.load_pct = 0;
    g.rpm = 0;
    g.oil = 0.0;
    g.p11_kw = 0.0;
    g.p15_rpm = 0;
  }
}
