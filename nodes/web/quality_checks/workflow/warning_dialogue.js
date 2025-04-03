import { $el, removeDialogueCloseButton } from "../../helpers/global/main.js";

const showWarningDialog = async (nodeList, message, canContinue = true) => {
  return new Promise((resolve) => {
    // Create a list of affected nodes
    const { dialogueTitle, dialogueMessage1, dialogueMessage2, dialogueMessage3 } = message;
    const nodesList = nodeList
      .map(
        (node) => `<li style="margin-left: 20px; margin-bottom: 5px;">${node.title || node.type} (ID: ${node.id})</li>`
      )
      .join("");

    const dialogContent = $el(
      "div",
      {
        style: {
          width: "90vw",
          maxWidth: "600px",
          padding: "20px",
          color: "white",
        },
      },
      [
        $el("h2", {
          style: {
            textAlign: "center",
            marginBottom: "20px",
            color: "#ff9900",
          },
          textContent: dialogueTitle,
        }),
        dialogueMessage1 &&
          $el("p", {
            style: { marginBottom: "15px" },
            innerHTML: dialogueMessage1,
          }),
        $el("ul", {
          style: {
            marginBottom: "20px",
            listStyleType: "disc",
          },
          innerHTML: nodesList,
        }),
        dialogueMessage2
          ? $el("p", {
              style: { marginBottom: "15px" },
              innerHTML: dialogueMessage2,
            })
          : $el("span", {}),
        dialogueMessage3
          ? $el("p", {
              style: { marginBottom: "20px" },
              innerHTML: dialogueMessage3,
            })
          : $el("span", {}),
        $el(
          "div",
          {
            style: {
              display: "flex",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "10px",
              marginTop: "30px",
            },
          },
          [
            $el("button", {
              textContent: "Cancel Submission",
              style: {
                padding: "10px 20px",
                backgroundColor: "#666",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                flex: "1",
                minWidth: "150px",
              },
              onclick: () => {
                const modalContent = document.querySelector(".comfy-modal-content");
                if (modalContent) {
                  const closeButton = modalContent.children.item(modalContent.children.length - 1);
                  if (closeButton) {
                    closeButton.style.display = "block";
                  }
                }
                app.ui.dialog.close();
                resolve({ continue: false });
              },
            }),
            canContinue
              ? $el("button", {
                  textContent: "Continue Anyway",
                  style: {
                    padding: "10px 20px",
                    backgroundColor: "#2D9CDB",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    flex: "1",
                    minWidth: "150px",
                  },
                  onclick: () => {
                    const modalContent = document.querySelector(".comfy-modal-content");
                    if (modalContent) {
                      const closeButton = modalContent.children.item(modalContent.children.length - 1);
                      if (closeButton) {
                        closeButton.style.display = "block";
                      }
                    }
                    app.ui.dialog.close();
                    resolve({ continue: true });
                  },
                })
              : $el("span", {}),
          ]
        ),
      ]
    );

    app.ui.dialog.show(dialogContent);
    removeDialogueCloseButton();
  });
};

export { showWarningDialog };
