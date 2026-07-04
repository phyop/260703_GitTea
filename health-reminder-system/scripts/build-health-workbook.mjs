import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = new URL("../outputs/", import.meta.url);
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const log = workbook.worksheets.add("Log");
const config = workbook.worksheets.add("Config");
const summary = workbook.worksheets.add("Summary");

const waterTimes = [
  "07:40",
  "08:45",
  "10:00",
  "11:00",
  "14:00",
  "15:15",
  "16:30",
  "17:45",
  "20:30",
  "21:45",
];

log.getRange("A1:Q1").values = [[
  "date",
  "water_ml",
  "water_cups",
  "vitamin_c",
  "vitamin_time",
  "bp_sys",
  "bp_dia",
  "weight_kg",
  "bp_weight_time",
  "last_water_time",
  "water_0740",
  "water_0845",
  "water_1000",
  "water_1100",
  "water_1400",
  "water_1515",
  "water_1630",
]];

log.getRange("R1:V1").values = [[
  "water_1745",
  "water_2030",
  "water_2145",
  "notes",
  "updated_at",
]];

for (let row = 2; row <= 32; row += 1) {
  log.getRange(`A${row}`).formulas = [[`=TODAY()+${row - 2}`]];
  log.getRange(`B${row}`).formulas = [[`=C${row}*250`]];
  log.getRange(`C${row}`).formulas = [[`=COUNTIF(K${row}:T${row},TRUE)`]];
}

config.getRange("A1:B1").values = [["key", "value"]];
config.getRange("A2:B19").values = [
  ["timezone", "Asia/Taipei"],
  ["water_ml_per_cup", 250],
  ["water_daily_cups", 10],
  ["water_daily_target_ml", 2500],
  ["water_times", waterTimes.join(",")],
  ["vitamin_main", "15:00"],
  ["vitamin_backup", "17:00"],
  ["bp_weight_main", "20:00"],
  ["bp_weight_backup", "21:30"],
  ["telegram_bot_token", "SET_IN_SCRIPT_PROPERTIES"],
  ["telegram_chat_id", "SET_IN_SCRIPT_PROPERTIES"],
  ["spreadsheet_id", "PASTE_THIS_SHEET_ID_IN_SCRIPT_PROPERTIES"],
  ["webhook_url", "SET_AFTER_DEPLOYMENT"],
  ["vitamin_backup_rule", "Only send at 17:00 if vitamin_c is not TRUE after 15:00."],
  ["bp_weight_backup_rule", "Only send at 21:30 if bp_sys, bp_dia, and weight_kg are not all recorded after 20:00."],
  ["water_schedule_1", waterTimes.slice(0, 5).join(",")],
  ["water_schedule_2", waterTimes.slice(5).join(",")],
  ["notes", "Do not store secrets in this sheet if you share it."],
];

summary.getRange("A1:E1").values = [["Metric", "Today", "Target", "Status", "Notes"]];
summary.getRange("A2:E6").values = [
  ["Water ml", null, 2500, null, "Daily target: 10 cups x 250 ml"],
  ["Water cups", null, 10, null, "Each checked cup counts as 250 ml"],
  ["Vitamin C", null, "TRUE", null, "Back-up reminder at 17:00 if missing"],
  ["Blood pressure", null, "Recorded", null, "Back-up reminder at 21:30 if missing"],
  ["Weight kg", null, "Recorded", null, "Logged with blood pressure"],
];
summary.getRange("B2:B6").formulas = [
  ["=IFERROR(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$B$2:$B$400),0)"],
  ["=IFERROR(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$C$2:$C$400),0)"],
  ["=IFERROR(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$D$2:$D$400),FALSE)"],
  ["=IF(AND(IFERROR(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$F$2:$F$400),\"\")<>\"\",IFERROR(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$G$2:$G$400),\"\")<>\"\"),TEXT(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$F$2:$F$400),\"0\")&\"/\"&TEXT(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$G$2:$G$400),\"0\"),\"\")"],
  ["=IFERROR(XLOOKUP(TODAY(),Log!$A$2:$A$400,Log!$H$2:$H$400),\"\")"],
];
summary.getRange("D2:D6").formulas = [
  ["=IF(B2>=C2,\"OK\",\"Pending\")"],
  ["=IF(B3>=C3,\"OK\",\"Pending\")"],
  ["=IF(B4=TRUE,\"OK\",\"Pending\")"],
  ["=IF(B5<>\"\",\"OK\",\"Pending\")"],
  ["=IF(B6<>\"\",\"OK\",\"Pending\")"],
];

for (const sheet of [log, config, summary]) {
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = true;
}

log.getRange("A1:V1").format = {
  fill: "#E5E7EB",
  font: { bold: true, color: "#111827" },
  wrapText: true,
};
config.getRange("A1:B1").format = {
  fill: "#E5E7EB",
  font: { bold: true, color: "#111827" },
};
summary.getRange("A1:E1").format = {
  fill: "#E5E7EB",
  font: { bold: true, color: "#111827" },
};

log.getRange("A:A").format.numberFormat = "yyyy-mm-dd";
log.getRange("B:C").format.numberFormat = "0";
log.getRange("F:G").format.numberFormat = "0";
log.getRange("H:H").format.numberFormat = "0.0";
log.getRange("A1:V32").format.borders = { preset: "inside", style: "thin", color: "#E5E7EB" };
config.getRange("A1:B19").format.borders = { preset: "inside", style: "thin", color: "#E5E7EB" };
summary.getRange("A1:E6").format.borders = { preset: "inside", style: "thin", color: "#E5E7EB" };

log.getRange("A:V").format.columnWidthPx = 112;
log.getRange("U:U").format.columnWidthPx = 220;
config.getRange("A:A").format.columnWidthPx = 190;
config.getRange("B:B").format.columnWidthPx = 520;
summary.getRange("A:E").format.columnWidthPx = 150;
summary.getRange("E:E").format.columnWidthPx = 260;

log.getRange("K2:T32").dataValidation = { rule: { type: "list", values: ["TRUE", "FALSE"] } };
log.getRange("D2:D32").dataValidation = { rule: { type: "list", values: ["TRUE", "FALSE"] } };

const inspect = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 4000,
  tableMaxRows: 5,
  tableMaxCols: 8,
});
console.log(inspect.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

const preview = await workbook.render({
  sheetName: "Summary",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(new URL("health-summary-preview.png", outputDir), new Uint8Array(await preview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(fileURLToPath(new URL("health-reminder-record-template.xlsx", outputDir)));
