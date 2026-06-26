const{
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageBreak, PageNumber, NumberFormat
} = require('docx');
const fs = require('fs');

const NAVY   = "1A2B4A";
const BLUE   = "2563EB";
const GRAY   = "6B7280";
const LIGHT  = "EFF6FF";
const WHITE  = "FFFFFF";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 180 },
    children: [new TextRun({ text, bold: true, size: 36, color: NAVY, font: "Arial" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 140 },
    children: [new TextRun({ text, bold: true, size: 28, color: BLUE, font: "Arial" })]
  });
}

function h3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, size: 24, color: NAVY, font: "Arial" })]
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: "374151", ...opts })]
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: "374151" })]
  });
}

function divider() {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "E5E7EB" } },
    children: []
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function cell(text, isHeader = false, width = 2340) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: { top: 100, bottom: 100, left: 150, right: 150 },
    shading: isHeader
      ? { fill: NAVY, type: ShadingType.CLEAR }
      : { fill: WHITE, type: ShadingType.CLEAR },
    children: [new Paragraph({
      children: [new TextRun({
        text,
        bold: isHeader,
        size: isHeader ? 20 : 20,
        font: "Arial",
        color: isHeader ? WHITE : "374151"
      })]
    })]
  });
}

function altCell(text, alt = false, width = 2340) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 150, right: 150 },
    shading: { fill: alt ? "F9FAFB" : WHITE, type: ShadingType.CLEAR },
    children: [new Paragraph({
      children: [new TextRun({ text, size: 20, font: "Arial", color: "374151" })]
    })]
  });
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: NAVY },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [

      
      new Paragraph({ spacing: { before: 1440, after: 200 }, children: [] }),

      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 80 },
        children: [new TextRun({ text: "INTERNSHIP PROJECT REPORT", bold: true, size: 48, font: "Arial", color: NAVY })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 400 },
        children: [new TextRun({ text: "Licence Manager Automation System", size: 32, font: "Arial", color: BLUE })]
      }),

      divider(),

      new Paragraph({ spacing: { before: 200, after: 80 }, children: [] }),

      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Submitted by: Gargi Kalia", size: 24, font: "Arial", color: "374151" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 60, after: 60 },
        children: [new TextRun({ text: "Internship Duration: May \u2013 June 2026", size: 22, font: "Arial", color: GRAY })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 60, after: 60 },
        children: [new TextRun({ text: "Technology Stack: Python \u00b7 FastAPI \u00b7 Jinja2 \u00b7 OpenPyXL \u00b7 JavaScript", size: 22, font: "Arial", color: GRAY })]
      }),

      pageBreak(),

      
      h1("1. Executive Summary"),
      p("This report documents the design, development, and delivery of the Licence Manager Automation System, built during my internship. The project automates a monthly manual task of extracting and computing multiple licence tables from a complex multi-header Excel file, previously done by hand."),
      p("The system accepts an input Excel file containing project-wise, department-wise, and location-wise licence data and automatically computes five output tables: Licence Summary, Department Lease Distribution, Sub Location Breakups, ISL (In-Stock Licences), and Keystore. It also provides a web-based frontend where users can interactively select software, input parameters, view computed tables, manage licence keys, and download the complete report."),

      divider(),

      
      h1("2. Problem Statement"),
      p("The team maintained an Excel file updated every month containing:"),
      bullet("Two locations (DTA and SEZ) with multiple projects under each"),
      bullet("Each project having department-wise LTC (Lease To Contractor) and Valdel licence numbers"),
      bullet("Summary columns for Own Licence, Lease Licence, and Total"),
      p("Every month, a team member had to manually extract five different types of licence tables from this file. This process was:"),
      bullet("Time-consuming \u2014 typically taking 2-3 hours"),
      bullet("Error-prone \u2014 manual calculations caused inconsistencies"),
      bullet("Not scalable \u2014 adding a new project or software required reworking all tables"),
      bullet("Undocumented \u2014 business rules for each table were known only to specific individuals"),

      divider(),

      h1("3. System Architecture"),
      p("The application follows a clean layered architecture separating parsing, computation, output generation, and routing concerns."),

      h2("3.1 Architecture Overview"),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2500, 6860],
        rows: [
          new TableRow({ children: [cell("Layer", true, 2500), cell("Responsibility", true, 6860)] }),
          new TableRow({ children: [altCell("Parser", false, 2500), altCell("Reads raw Excel, unmerges cells, detects columns dynamically, extracts records", false, 6860)] }),
          new TableRow({ children: [altCell("Table Builder", true, 2500), altCell("Computes all 5 table types using business rules", true, 6860)] }),
          new TableRow({ children: [altCell("Excel Writer", false, 2500), altCell("Writes computed tables as formatted sheets to output Excel file", false, 6860)] }),
          new TableRow({ children: [altCell("Routers", true, 2500), altCell("FastAPI endpoints exposing upload, tables, keystore, and download APIs", true, 6860)] }),
          new TableRow({ children: [altCell("Session", false, 2500), altCell("In-memory session management for parsed data within one usage session", false, 6860)] }),
          new TableRow({ children: [altCell("Frontend", true, 2500), altCell("Jinja2 templates with vanilla JavaScript for UI interactions", true, 6860)] }),
        ]
      }),

      new Paragraph({ spacing: { before: 200 }, children: [] }),

      h2("3.2 Data Flow"),
      p("The system data flow follows these sequential steps:"),
      bullet("User uploads .xlsx file via the web interface"),
      bullet("Parser unmerges all merged cells and saves to a temporary file"),
      bullet("Parser dynamically detects header rows, project columns (by scanning for LTC headers), and summary columns (Own Lic, Lease Lic, Total)"),
      bullet("Records are extracted with developer/software/dept metadata using forward-fill for merged rows"),
      bullet("Parsed data is stored in a server-side session keyed by session ID"),
      bullet("User selects developers, software, and provides input values (Annual, Advent, Onshore) on the Dashboard"),
      bullet("Report page computes all 4 tables per software using per-software inputs"),
      bullet("Keystore table is computed using business-rule calculator and user-provided values"),
      bullet("Download endpoint builds all tables and writes to a formatted Excel report with 5 sheets"),

      h2("3.3 Folder Structure"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3200, 6160],
        rows: [
          new TableRow({ children: [cell("File / Folder", true, 3200), cell("Purpose", true, 6160)] }),
          new TableRow({ children: [altCell("services/parser.py", false, 3200), altCell("Excel parsing, unmerging, column detection, record extraction", false, 6160)] }),
          new TableRow({ children: [altCell("services/table_builder.py", true, 3200), altCell("All 5 table computation functions and keystore calculator", true, 6160)] }),
          new TableRow({ children: [altCell("services/excel_writer.py", false, 3200), altCell("Writes 5 formatted output sheets to Excel workbook", false, 6160)] }),
          new TableRow({ children: [altCell("routers/upload.py", true, 3200), altCell("POST /upload \u2014 file ingestion and session creation", true, 6160)] }),
          new TableRow({ children: [altCell("routers/tables.py", false, 3200), altCell("GET endpoints for all 4 table types + developer/software lists", false, 6160)] }),
          new TableRow({ children: [altCell("routers/keystore.py", true, 3200), altCell("GET /keystore/table, POST toggle and add key endpoints", true, 6160)] }),
          new TableRow({ children: [altCell("routers/download.py", false, 3200), altCell("POST /download \u2014 builds all tables and returns Excel file", false, 6160)] }),
          new TableRow({ children: [altCell("core/session.py", true, 3200), altCell("In-memory session store with 8-hour expiry", true, 6160)] }),
          new TableRow({ children: [altCell("core/errors.py", false, 3200), altCell("Custom exception classes and global FastAPI error handlers", false, 6160)] }),
          new TableRow({ children: [altCell("core/keystore.py", true, 3200), altCell("JSON-based keystore persistence (load, save, toggle, add)", true, 6160)] }),
          new TableRow({ children: [altCell("data/keystore_keys.json", false, 3200), altCell("Persisted keystore key registry, survives server restarts", false, 6160)] }),
          new TableRow({ children: [altCell("templates/", true, 3200), altCell("Jinja2 HTML templates for all pages", true, 6160)] }),
          new TableRow({ children: [altCell("static/app.js + style.css", false, 3200), altCell("Shared JavaScript utilities and professional CSS design system", false, 6160)] }),
        ]
      }),

      pageBreak(),

      
      h1("4. Technology Stack"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2800, 3280, 3280],
        rows: [
          new TableRow({ children: [cell("Technology", true, 2800), cell("Version", true, 3280), cell("Usage", true, 3280)] }),
          new TableRow({ children: [altCell("Python", false, 2800), altCell("3.11+", false, 3280), altCell("Core backend language", false, 3280)] }),
          new TableRow({ children: [altCell("FastAPI", true, 2800), altCell("Latest", true, 3280), altCell("REST API framework with auto-docs", true, 3280)] }),
          new TableRow({ children: [altCell("OpenPyXL", false, 2800), altCell("3.x", false, 3280), altCell("Excel read/write/formatting", false, 3280)] }),
          new TableRow({ children: [altCell("Jinja2", true, 2800), altCell("3.x", true, 3280), altCell("Server-side HTML templating", true, 3280)] }),
          new TableRow({ children: [altCell("Uvicorn", false, 2800), altCell("Latest", false, 3280), altCell("ASGI server for FastAPI", false, 3280)] }),
          new TableRow({ children: [altCell("Pydantic", true, 2800), altCell("v2", true, 3280), altCell("Request/response validation", true, 3280)] }),
          new TableRow({ children: [altCell("Vanilla JavaScript", false, 2800), altCell("ES2020+", false, 3280), altCell("Frontend interactivity, sessionStorage", false, 3280)] }),
          new TableRow({ children: [altCell("CSS (custom)", true, 2800), altCell("\u2014", true, 3280), altCell("Navy design system, no framework", true, 3280)] }),
          new TableRow({ children: [altCell("JSON", false, 2800), altCell("\u2014", false, 3280), altCell("Keystore persistence (no database)", false, 3280)] }),
        ]
      }),

      new Paragraph({ spacing: { before: 200 }, children: [] }),

      divider(),

      
      h1("5. Key Features Implemented"),

      h2("5.1 Intelligent Excel Parser"),
      bullet("Handles merged cells by unmerging and filling all cells with the top-left value before parsing"),
      bullet("Dynamically detects project columns by scanning for LTC headers \u2014 works regardless of how many projects are added or removed each month"),
      bullet("Detects summary columns (Own Lic, Lease Lic, Total) by keyword matching"),
      bullet("Uses forward-fill (ffill) logic for Developer and Software columns that span multiple rows"),
      bullet("Reads own/lease/total values from the summary row at the bottom of each software group"),

      h2("5.2 Five Computed Output Tables"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2800, 6560],
        rows: [
          new TableRow({ children: [cell("Table", true, 2800), cell("Description", true, 6560)] }),
          new TableRow({ children: [altCell("Licence Summary", false, 2800), altCell("Per-software totals with Annual and Order computation. Order = Lease \u2212 Annual. Advent value added for SP3D.", false, 6560)] }),
          new TableRow({ children: [altCell("Dept Lease Distribution", true, 2800), altCell("Allocates licences across NPP, PP, CV categories. Advent and Onshore are user-provided additions.", true, 6560)] }),
          new TableRow({ children: [altCell("Sub Location Breakups", false, 2800), altCell("Computes Valdel, PP, CEC (sum of Others), VEC (Order \u2212 CEC). Location-wise licence ordering.", false, 6560)] }),
          new TableRow({ children: [altCell("ISL", true, 2800), altCell("Dept-wise breakdown of In-Stock Licences as LTM (integer part) and Share (decimal part).", true, 6560)] }),
          new TableRow({ children: [altCell("Keystore", false, 2800), altCell("Key ID registry per software and department. Values computed by calculator or entered by user. Validates against order limits.", false, 6560)] }),
        ]
      }),

      new Paragraph({ spacing: { before: 200 }, children: [] }),

      h2("5.3 Keystore Management"),
      bullet("Keys stored in keystore_keys.json \u2014 persists across server restarts"),
      bullet("Active/inactive toggle per key, saved immediately to JSON"),
      bullet("New keys can be added for any software and department combination"),
      bullet("Keystore values validated against: global Order limit (sum of all active keys \u2264 Order), and per-label limits from Allocated (NPP, PP, CV) and Required (CEC, VEC) tables"),
      bullet("Immediate red highlighting when a user-typed value causes the sum to exceed limits"),

      h2("5.4 Per-Software Input System"),
      bullet("Dashboard allows selection of multiple developers and their respective software"),
      bullet("Each selected software has its own Annual, Onshore inputs; Advent appears only for SP3D"),
      bullet("Inputs saved to browser sessionStorage and used per-software when computing tables"),
      bullet("Report page shows all 4 tables in software tabs \u2014 one tab per selected software"),

      divider(),
      pageBreak(),

      
      h1("6. Challenges & Solutions"),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3600, 2880, 2880],
        rows: [
          new TableRow({ children: [cell("Challenge", true, 3600), cell("Root Cause", true, 2880), cell("Solution", true, 2880)] }),
          new TableRow({
            children: [
              altCell("Merged cells returning None for non-top-left cells in OpenPyXL", false, 3600),
              altCell("OpenPyXL reads merged ranges with only the first cell populated", false, 2880),
              altCell("Unmerge all ranges first, then fill every cell with the top-left value before any parsing", false, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("Project columns were hardcoded by cell position (e.g. ws['D4'])", true, 3600),
              altCell("Number of projects changes monthly, breaking hardcoded references", true, 2880),
              altCell("Dynamic detection: scan header row for LTC headers, derive project metadata from rows above", true, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("Session expiring immediately (diff_seconds = -7)", false, 3600),
              altCell("timedelta() was receiving seconds instead of hours as positional argument", false, 2880),
              altCell("Changed to explicit keyword argument: timedelta(hours=SESSION_EXPIRY_HOURS)", false, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("MergedCell objects raising AttributeError when assigning .value", true, 3600),
              altCell("After unmerge(), iterating with iter_rows() still returned stale MergedCell objects", true, 2880),
              altCell("Access cells using ws.cell(row=x, column=y) after unmerge instead of iter_rows", true, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("grand_ltc accumulation was inside wrong conditional block", false, 3600),
              altCell("grand_ltc += ltc_v was nested inside if total_p_col is not None", false, 2880),
              altCell("Moved grand_ltc += ltc_v outside the conditional to always accumulate", false, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("Developer list returning all names as one comma-separated string", true, 3600),
              altCell("get_developer_list() used return[{set comprehension}] wrapping set in a list", true, 2880),
              altCell("Fixed to return list({data['developer'] ...}) without extra brackets", true, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("Own/lease/total values repeating incorrectly across all dept rows", false, 3600),
              altCell("aggregate_by_software() was using += for own_lic/lease_lic summing across depts", false, 2880),
              altCell("Added seen_sw set to set own/lease/total only once per software from the total row", false, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("Download creating duplicate _report suffix in output filename", true, 3600),
              altCell("get_output_path() appending _report to filenames that already contained _report", true, 2880),
              altCell("Strip existing _report suffix before appending: base.replace('_report.xlsx', '.xlsx')", true, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("CSS variables not resolving in dynamically injected inline styles", false, 3600),
              altCell("var(--accent) in template literals inside JS innerHTML is not evaluated by browser", false, 2880),
              altCell("Replaced all CSS variable references with hardcoded hex values in JS strings", false, 2880)
            ]
          }),
          new TableRow({
            children: [
              altCell("TypeError: unhashable type: dict in TemplateResponse", true, 3600),
              altCell("Jinja2 TemplateResponse called with arguments in wrong order", true, 2880),
              altCell("Fixed argument order: TemplateResponse(request=request, name='file.html')", true, 2880)
            ]
          }),
        ]
      }),

      pageBreak(),

     
      h1("7. Validation & Testing"),

      h2("7.1 Parser Validation"),
      bullet("Tested with the actual Book1.xlsx file provided by the team"),
      bullet("Verified all 5 projects detected correctly, with dynamic column detection skipping the LTC summary column"),
      bullet("Confirmed ffill logic correctly propagates Developer and Software across department rows"),
      bullet("Verified own/lease/total values read from the total row and not accumulated across depts"),

      h2("7.2 API Validation"),
      bullet("All endpoints tested via FastAPI /docs Swagger UI"),
      bullet("Upload endpoint returns session ID, project count, software list, and record count"),
      bullet("Table endpoints verified to return correct computed values matching manual calculations"),
      bullet("Download endpoint produces valid Excel file with 5 correctly formatted sheets"),
      bullet("Keystore toggle and add endpoints verified to persist correctly to JSON file"),

      h2("7.3 Frontend Validation"),
      bullet("Dashboard developer cards render as separate clickable elements"),
      bullet("Software cards show individual input fields with Advent appearing only for SP3D"),
      bullet("Report page software tabs load all 4 tables independently per software"),
      bullet("Keystore validation highlights exceeded limits in red immediately on input"),
      bullet("Download triggers file save with all per-software inputs applied correctly"),

      divider(),

      h1("8. Limitations & Future Scope"),

      h2("8.1 Current Limitations"),
      bullet("Session data is in-memory only \u2014 a server restart requires re-uploading the file"),
      bullet("Keystore calculator business rules are hardcoded per software name \u2014 requires code change for new software"),
      bullet("No user authentication \u2014 suitable for internal single-user use only"),
      bullet("Edit mode on tables saves values locally in the browser but does not send them back to the computed Excel output"),

      h2("8.2 Future Enhancements"),
      bullet("Persist sessions to disk (JSON or SQLite) so uploads survive server restarts"),
      bullet("Make keystore calculator rules configurable via a UI or config file rather than hardcoded"),
      bullet("Add user authentication for multi-user support"),
      bullet("Send edited table values back to the download endpoint so the Excel reflects user edits"),
      bullet("Add email notification when the monthly report is generated"),
      bullet("Build a comparison view to show month-over-month licence changes"),

      divider(),

     
      h1("9. Conclusion"),
      p("The Licence Manager Automation System successfully automates the monthly manual licence reporting task. The system is designed to be generalised \u2014 it dynamically detects Excel structure rather than relying on hardcoded cell positions, which means it handles changes in the number of projects or departments without any code modification."),
      p("The project demonstrates a full-stack implementation covering intelligent data parsing, REST API design with proper error handling, session management, formatted Excel output generation, and a professional web frontend. The system reduces the monthly reporting effort from several hours to under five minutes."),
      p("This internship project provided hands-on experience with production-grade Python backend development, FastAPI architecture patterns, Excel automation with OpenPyXL, and frontend development with vanilla JavaScript and Jinja2 templating."),

      divider(),

      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400, after: 0 },
        children: [new TextRun({ text: "Gargi Kalia \u00b7 Internship Project \u00b7 2026", size: 18, font: "Arial", color: GRAY, italics: true })]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/mnt/user-data/outputs/Licence_Manager_Internship_Report.docx', buffer);
  console.log('Done');
});