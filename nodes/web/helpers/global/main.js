import { app } from "../../../../scripts/app.js";

const showMessage = (message, color, detailedInfo = null, backgroundColor = "#00000000", extraBody = null) => {
  let dialogContent = `
        <div style="
          text-align: center;
          padding: 20px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          width: 100%;
        ">
          <div style="
            display: flex;
            align-items: center;
            gap: 20px;
          ">
            ${extraBody || ""}
            <p style="
              color: ${color};
              font-size: 20px;
              margin: 0;
              text-align: center;
              background-color: ${backgroundColor};
            ">
              ${message}
            </p>
          </div>
          ${
            detailedInfo
              ? `
            <pre style="
              text-align: left;
              white-space: pre-wrap;
              margin: 0;
              background-color: rgba(0, 0, 0, 0.3);
              padding: 10px;
              border-radius: 4px;
              width: 100%;
            ">${detailedInfo}</pre>
          `
              : ""
          }
        </div>`;

  app.ui.dialog.show(dialogContent);
};

export { showMessage };
