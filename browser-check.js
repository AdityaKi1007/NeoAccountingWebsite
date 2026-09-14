const { chromium } = require("/opt/node-tools/node_modules/playwright");
const path = require("path");

(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("console", (msg) => { if (msg.type() === "error") errors.push("console.error: " + msg.text()); });

  const fileUrl = "file://" + path.resolve(__dirname, "full-doc-v3-preview.html");
  await page.goto(fileUrl, { waitUntil: "load" });

  // Confirm the adversarial signup data actually parsed into the live DOM
  // exactly as expected -- the strongest possible proof a real browser
  // engine (not just our regex simulation) handled it safely.
  const count = await page.evaluate(() => {
    const el = document.getElementById("signups-data");
    return JSON.parse(el.textContent).length;
  });
  console.log("signups parsed by real browser DOM:", count);
  if (count !== 2) throw new Error("expected 2 signups in the live DOM, got " + count);

  // Visual check.
  await page.setViewportSize({ width: 1280, height: 1600 });
  await page.screenshot({ path: "screenshot-desktop-light.png", fullPage: true });
  await page.setViewportSize({ width: 400, height: 900 });
  await page.screenshot({ path: "screenshot-mobile.png", fullPage: true });
  await page.emulateMedia({ colorScheme: "dark" });
  await page.setViewportSize({ width: 1280, height: 1600 });
  await page.screenshot({ path: "screenshot-desktop-dark.png", fullPage: true });

  // Ignore this sandbox's own egress-proxy restrictions (it blocks
  // fonts.googleapis.com locally; the real claude.ai artifact host allows
  // it) -- not a defect in the page itself.
  const realErrors = errors.filter((e) => !/ERR_TUNNEL_CONNECTION_FAILED|ERR_NAME_NOT_RESOLVED|fonts\.(googleapis|gstatic)\.com/.test(e));
  console.log("console/page errors:", errors.length ? errors : "none");
  if (realErrors.length) throw new Error("browser reported errors: " + realErrors.join(" | "));

  await browser.close();
  console.log("Browser check passed.");
})().catch((e) => { console.error(e); process.exit(1); });
