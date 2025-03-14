const setColorAndBgColor = (type) => {
  const colorMap = {
    MODEL: LGraphCanvas.node_colors.blue,
    LATENT: LGraphCanvas.node_colors.purple,
    VAE: LGraphCanvas.node_colors.red,
    CONDITIONING: LGraphCanvas.node_colors.brown,
    IMAGE: LGraphCanvas.node_colors.pale_blue,
    CLIP: LGraphCanvas.node_colors.yellow,
    FLOAT: LGraphCanvas.node_colors.green,
    MASK: { color: "#1c5715", bgcolor: "#1f401b" },
    INT: { color: "#1b4669", bgcolor: "#29699c" },
    CONTROL_NET: { color: "#156653", bgcolor: "#1c453b" },
    NOISE: { color: "#2e2e2e", bgcolor: "#242121" },
    GUIDER: { color: "#3c7878", bgcolor: "#1c453b" },
    SAMPLER: { color: "#614a4a", bgcolor: "#3b2c2c" },
    SIGMAS: { color: "#485248", bgcolor: "#272e27" },
  };

  const colors = colorMap[type];
  if (colors) {
    this.color = colors.color;
    this.bgcolor = colors.bgcolor;
  }
};

export { setColorAndBgColor };
