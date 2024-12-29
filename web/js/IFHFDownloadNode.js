const { app } = window.comfyAPI.app;

// Load CSS
//const link = document.createElement('link');
//link.rel = 'stylesheet';
//link.type = 'text/css';
//link.href = 'file=ComfyUI-IF_AI_HFDownloaderNode/web/js/IFHFDownload.css';
//document.head.appendChild(link);

app.registerExtension({
    name: "IFHFDownload",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass === "IF_HFDownload") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated?.apply(this, arguments);
                
                this.element.classList.add('IF-HFDownload-node');

                // Add download button
                this.addWidget("button", "Download", "download", () => {
                    this.downloadFiles();
                });

                // Add progress bar
                this.addWidget("progressbar", "Progress", "progress", 0, 1);
                this.progressBarWidget = this.widgets[this.widgets.length - 1];
                this.progressBarWidget.classList?.add("IF-progress-bar");

                // Add titles to each input
                this.inputs.forEach(input => {
                    const widget = this.widgets.find(w => w.name === input.name);
                    if (widget) {
                        const title = document.createElement("div");
                        title.className = "IF-input-title";
                        title.textContent = this.getInputTitle(input.name);
                        widget.element.parentNode.insertBefore(title, widget.element);
                    }
                });
            };

            nodeType.prototype.getInputTitle = function(inputName) {
                const titles = {
                    repo_id: "Repository ID",
                    file_paths: "File Paths",
                    folder_path: "Download Folder",
                    exclude_files: "Exclude Files",
                    hf_token: "HF Token",
                    mode: "Download Mode"
                };
                return titles[inputName] || inputName;
            };

            nodeType.prototype.downloadFiles = async function() {
                const data = {
                    mode: this.widgets.find(w => w.name === "mode").value,
                    repo_id: this.widgets.find(w => w.name === "repo_id").value,
                    file_paths: this.widgets.find(w => w.name === "file_paths").value,
                    folder_path: this.widgets.find(w => w.name === "folder_path").value,
                    exclude_files: this.widgets.find(w => w.name === "exclude_files").value,
                    hf_token: this.widgets.find(w => w.name === "hf_token").value,
                };

                try {
                    const response = await fetch("/custom_node/hf_download", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(data)
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    this.output = result.result;
                    app.ui.dialog.show(`Download Complete: ${this.output}`);
                } catch (error) {
                    console.error("Download failed:", error);
                    app.ui.dialog.show("Download failed. Check console for details.");
                }
            };

            // Handle progress updates
            nodeType.prototype.onExecuted = function(message) {
                if (message.progress !== undefined) {
                    this.progressBarWidget.value = message.progress.value;
                    this.progressBarWidget.max = message.progress.max;
                    if (message.progress.text) {
                        this.progressBarWidget.innerText = message.progress.text;
                    }
                    this.setDirtyCanvas(true, false);
                }
            };

            // Update widget values when node is loaded
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                onConfigure?.apply(this, arguments);
                for (const w of this.widgets) {
                    if (w.type !== "button" && info[w.name] !== undefined) {
                        w.value = info[w.name];
                    }
                }
            };
        }
    }
});