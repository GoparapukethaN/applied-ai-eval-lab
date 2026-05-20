import { chromium } from "@playwright/test";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(__dirname, "..");
const outDir = path.join(frontendDir, "out");
const basePath = "/applied-ai-eval-lab";
const externalUrl = process.env.AIEL_STATIC_DEMO_URL;

function contentType(filePath) {
  if (filePath.endsWith(".html")) return "text/html; charset=utf-8";
  if (filePath.endsWith(".js")) return "text/javascript; charset=utf-8";
  if (filePath.endsWith(".css")) return "text/css; charset=utf-8";
  if (filePath.endsWith(".svg")) return "image/svg+xml";
  if (filePath.endsWith(".png")) return "image/png";
  if (filePath.endsWith(".jpg") || filePath.endsWith(".jpeg")) return "image/jpeg";
  if (filePath.endsWith(".txt")) return "text/plain; charset=utf-8";
  return "application/octet-stream";
}

async function fileExists(filePath) {
  try {
    await stat(filePath);
    return true;
  } catch {
    return false;
  }
}

async function resolveStaticPath(urlPath) {
  let relativePath = decodeURIComponent(urlPath.split("?")[0] || "/");
  if (relativePath === "/") relativePath = `${basePath}/`;
  if (relativePath === basePath) relativePath = `${basePath}/`;
  if (relativePath.startsWith(`${basePath}/`)) {
    relativePath = relativePath.slice(basePath.length);
  }
  if (relativePath === "/") relativePath = "/index.html";

  const candidate = path.normalize(path.join(outDir, relativePath));
  if (!candidate.startsWith(outDir)) {
    return null;
  }
  if (await fileExists(candidate)) {
    return candidate;
  }
  const htmlCandidate = path.join(candidate, "index.html");
  if (await fileExists(htmlCandidate)) {
    return htmlCandidate;
  }
  return null;
}

function startStaticServer() {
  const server = createServer(async (request, response) => {
    const filePath = await resolveStaticPath(request.url ?? "/");
    if (!filePath) {
      response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("not found");
      return;
    }
    const body = await readFile(filePath);
    response.writeHead(200, { "Content-Type": contentType(filePath) });
    response.end(body);
  });

  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      if (!address || typeof address === "string") {
        reject(new Error("static server did not expose a TCP port"));
        return;
      }
      resolve({ server, url: `http://127.0.0.1:${address.port}${basePath}/` });
    });
  });
}

async function verifyViewport(browser, url, viewport) {
  const page = await browser.newPage({ viewport });
  const consoleIssues = [];
  page.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) {
      consoleIssues.push(`${message.type()}: ${message.text()}`);
    }
  });
  page.on("pageerror", (error) => {
    consoleIssues.push(`pageerror: ${error.message}`);
  });

  await page.goto(url, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Index" }).click();
  await page.getByRole("button", { name: "Run Query" }).click();
  await page.getByRole("button", { name: "Run Eval" }).click();
  await page.getByRole("button", { name: "Compare" }).click();
  await page.waitForTimeout(250);

  const bodyText = await page.locator("body").innerText();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  );

  const requiredText = [
    "Applied AI Eval Lab",
    "CHUNKS",
    "5",
    "Evaluation reports should include answer quality",
    "Release gate: PASS",
    "Balanced Retrieval",
  ];
  for (const text of requiredText) {
    if (!bodyText.includes(text)) {
      throw new Error(`missing expected text in ${viewport.width}px viewport: ${text}`);
    }
  }
  if (overflow) {
    throw new Error(`horizontal overflow in ${viewport.width}px viewport`);
  }
  if (consoleIssues.length > 0) {
    throw new Error(`console issues in ${viewport.width}px viewport:\n${consoleIssues.join("\n")}`);
  }

  await page.close();
  console.log(`static demo QA passed at ${viewport.width}x${viewport.height}`);
}

let server;
try {
  const target = externalUrl ?? await startStaticServer();
  const url = typeof target === "string" ? target : target.url;
  server = typeof target === "string" ? undefined : target.server;
  const browser = await chromium.launch();
  try {
    await verifyViewport(browser, url, { width: 1440, height: 1000 });
    await verifyViewport(browser, url, { width: 390, height: 844 });
  } finally {
    await browser.close();
  }
} finally {
  if (server) {
    await new Promise((resolve) => server.close(resolve));
  }
}
