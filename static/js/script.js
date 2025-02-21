document
  .getElementById("convertForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();
    const url = document.getElementById("url").value;
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Fetching available formats...</p>";

    try {
      const response = await fetch("/convert", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `url=${encodeURIComponent(url)}`,
      });

      const data = await response.json();
      if (data.error) {
        resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
      }

      // Display the available formats
      displayFormats(data.formats);
    } catch (error) {
      resultsDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
  });

function displayFormats(formats) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";

  const mp3Container = document.createElement("div");
  mp3Container.innerHTML = "<h3>🎵 MP3 Options</h3>";
  const mp4Container = document.createElement("div");
  mp4Container.innerHTML = "<h3>🎬 MP4 Options</h3>";

  // Filter MP3 formats
  const mp3Formats = formats.filter((f) => f.type === "mp3");

  // Filter MP4 formats for specific resolutions and remove duplicates
  const desiredResolutions = ["640x360", "854x480", "1280x720"];
  const uniqueMp4Formats = {};

  formats
    .filter((f) => f.type === "mp4" && desiredResolutions.includes(f.quality))
    .forEach((format) => {
      if (!uniqueMp4Formats[format.quality]) {
        uniqueMp4Formats[format.quality] = format;
      }
    });

  // Display MP3 Options
  mp3Formats.forEach((format) => {
    const box = document.createElement("div");
    box.classList.add("format-box");
    box.innerHTML = `
      <p><strong>${format.quality} MP3</strong></p>
      <button onclick="downloadFormat('${format.itag}', 'mp3')">⬇️ Download</button>
    `;
    mp3Container.appendChild(box);
  });

  // Display Unique MP4 Options (360p, 480p, 720p)
  Object.values(uniqueMp4Formats).forEach((format) => {
    const box = document.createElement("div");
    box.classList.add("format-box");
    box.innerHTML = `
      <p><strong>${format.quality} MP4</strong></p>
      <button onclick="downloadFormat('${format.itag}', 'mp4')">⬇️ Download</button>
    `;
    mp4Container.appendChild(box);
  });

  resultsDiv.appendChild(mp3Container);
  resultsDiv.appendChild(mp4Container);
}

async function downloadFormat(itag, format) {
  const url = document.getElementById("url").value;
  const resultsDiv = document.getElementById("results");

  try {
    resultsDiv.innerHTML += `<p>Downloading ${format}...</p>`;

    const response = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `url=${encodeURIComponent(url)}&itag=${itag}&format=${format}`,
    });

    if (!response.ok) throw new Error("Failed to download");

    const blob = await response.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `download.${format}`;
    link.click();

    resultsDiv.innerHTML += `<p style="color: green;">Download complete!</p>`;
  } catch (error) {
    resultsDiv.innerHTML += `<p style="color: red;">Error: ${error.message}</p>`;
  }
}
