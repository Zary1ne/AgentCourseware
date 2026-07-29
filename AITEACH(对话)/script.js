// ============================================
// AI 教学助手 - 前端
// ============================================

(function() {
    "use strict";

    var messageInput = document.getElementById("messageInput");
    var sendBtn = document.getElementById("sendBtn");
    var messagesContainer = document.getElementById("messagesContainer");
    var stopBtn = document.getElementById("stopBtn");
    var starsBg = document.getElementById("starsBg");

    var scrollNav = null;

    if (!messageInput || !sendBtn || !messagesContainer) return;

    var isTyping = false;
    var abortController = null;
    var userAtBottom = true;
    var SCROLL_THRESHOLD = 80;

    function createStars() {
        if (!starsBg) return;
        var starCount = 100;
        for (var i = 0; i < starCount; i++) {
            var star = document.createElement("div");
            var sizes = ["small", "medium", "large"];
            var size = sizes[Math.floor(Math.random() * sizes.length)];
            star.className = "star " + size;
            star.style.left = Math.random() * 100 + "%";
            star.style.top = Math.random() * 100 + "%";
            star.style.animationDelay = Math.random() * 3 + "s";
            star.style.animationDuration = (2 + Math.random() * 3) + "s";
            starsBg.appendChild(star);
        }
    }

    function createScrollNav() {
        if (scrollNav) return;
        scrollNav = document.createElement("div");
        scrollNav.className = "scroll-nav";
        var panelCenter = document.querySelector(".panel-center");
        if (panelCenter) {
            panelCenter.appendChild(scrollNav);
        } else {
            document.body.appendChild(scrollNav);
        }
    }

    function updateScrollNav() {
        if (!scrollNav) return;
        
        var userMessages = messagesContainer.querySelectorAll(".msg-user");
        scrollNav.innerHTML = "";
        
        userMessages.forEach(function(msg) {
            var dot = document.createElement("div");
            dot.className = "scroll-dot";
            dot.onclick = function() {
                msg.scrollIntoView({ behavior: "smooth", block: "center" });
            };
            scrollNav.appendChild(dot);
        });
    }

    function onScroll() {
        var scrollBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop - messagesContainer.clientHeight;
        userAtBottom = scrollBottom < SCROLL_THRESHOLD;
        
        if (!scrollNav) return;
        
        var userMessages = messagesContainer.querySelectorAll(".msg-user");
        var dots = scrollNav.querySelectorAll(".scroll-dot");
        var containerTop = messagesContainer.getBoundingClientRect().top;
        
        var activeIndex = -1;
        userMessages.forEach(function(msg, index) {
            var msgTop = msg.getBoundingClientRect().top - containerTop;
            if (msgTop <= 150 && msgTop >= -150) {
                activeIndex = index;
            }
        });
        
        dots.forEach(function(dot, index) {
            if (index === activeIndex) {
                dot.classList.add("active");
            } else {
                dot.classList.remove("active");
            }
        });
    }

    async function checkHealth() {
        try {
            var resp = await fetch("/api/v1/health");
            var data = await resp.json();
            if (data.status === "ok") {
                messagesContainer.classList.add("connected");
            }
        } catch(e) {
            console.error("Health check failed:", e);
        }
    }

    function detectExportType(userText) {
        var t = userText.toLowerCase();
        if (/ppt|课件|幻灯片|演示文稿|powerpoint|presentation/.test(t)) return "pptx";
        if (/教案|word|文档|docx|教学设计|方案|导学案|教学目标|教学方案/.test(t)) return "docx";
        return null;
    }

    function escapeHtml(t) {
        var d = document.createElement("div");
        d.textContent = t;
        return d.innerHTML;
    }

    function scrollToBottom() {
        if (userAtBottom) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    function autoResize() {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
    }

    function updateSendButton() {
        sendBtn.disabled = messageInput.value.trim().length === 0 || isTyping;
    }

    function hideWelcome() {
        var welcomeSection = document.getElementById("welcomeSection");
        if (welcomeSection && !welcomeSection.classList.contains("hidden")) {
            welcomeSection.classList.add("hidden");
        }
    }

    function addUserMessage(text) {
        var el = document.createElement("div");
        el.className = "message msg-user";
        el.innerHTML = '<div class="msg-avatar"><svg viewBox="0 0 48 48"><rect x="8" y="10" width="32" height="34" rx="4"/><ellipse cx="24" cy="22" rx="10" ry="8"/><circle cx="18" cy="20" r="2"/><circle cx="30" cy="20" r="2"/><path d="M18 26 Q24 32 30 26"/><rect x="10" y="36" width="8" height="6" rx="2"/><rect x="30" y="36" width="8" height="6" rx="2"/></svg></div><div class="msg-body"><div class="msg-content">' + escapeHtml(text) + '</div></div>';
        messagesContainer.appendChild(el);
        hideWelcome();
        scrollToBottom();
        updateScrollNav();
    }

    function createAIBubble() {
        var el = document.createElement("div");
        el.className = "message msg-assistant";
        el.innerHTML = '<div class="msg-avatar"><svg viewBox="0 0 48 48"><ellipse cx="24" cy="24" rx="16" ry="14"/><circle cx="24" cy="20" r="6"/><circle cx="24" cy="19" r="2"/><line x1="24" y1="35" x2="18" y2="45"/><line x1="24" y1="35" x2="30" y2="45"/><line x1="24" y1="10" x2="24" y2="4"/><line x1="20" y1="11" x2="18" y2="5"/><line x1="28" y1="11" x2="30" y2="5"/></svg></div><div class="msg-body"><div class="msg-content-wrap"></div></div>';
        messagesContainer.appendChild(el);
        scrollToBottom();
        return el.querySelector(".msg-content-wrap");
    }

    function appendStreamChar(body, char) {
        var contentDiv = body.querySelector(".msg-content");
        if (!contentDiv) {
            body.innerHTML = '<div class="msg-content"></div><span class="typing-cursor"></span>';
            contentDiv = body.querySelector(".msg-content");
        }
        if (char === "\n") {
            contentDiv.appendChild(document.createElement("br"));
        } else {
            contentDiv.appendChild(document.createTextNode(char));
        }
        scrollToBottom();
    }

    function appendThinkingChar(body, char) {
        var thinkingSection = body.querySelector(".thinking-section");
        if (!thinkingSection) {
            body.innerHTML = '<div class="thinking-section collapsed" onclick="this.classList.toggle(\'expanded\');"><div class="thinking-toggle"><span class="thinking-toggle-icon">\u25B6</span><span>思考过程</span></div><div class="thinking-content"></div></div>' + body.innerHTML;
            thinkingSection = body.querySelector(".thinking-section");
        }
        var thinkingContent = body.querySelector(".thinking-content");
        thinkingContent.appendChild(document.createTextNode(char));
    }

    function finishMessage(body) {
        var cursor = body.querySelector(".typing-cursor");
        if (cursor) cursor.remove();
        
        var thinkingSection = body.querySelector(".thinking-section");
        if (thinkingSection && thinkingSection.querySelector(".thinking-content").textContent.trim() === "") {
            thinkingSection.remove();
        }
    }

    function showError(body, msg) {
        body.innerHTML = '<div class="msg-content"><p style="color:#ef4444;font-size:13px;margin-top:8px">\u274C ' + escapeHtml(msg) + '</p></div>';
    }

    function addExportButtons(body, exportType, userText) {
        var existing = body.querySelector(".export-buttons");
        if (existing) existing.remove();

        var container = document.createElement("div");
        container.className = "export-buttons";

        if (exportType === "docx") {
            var btnDocx = document.createElement("button");
            btnDocx.className = "btn-export btn-export-docx";
            btnDocx.innerHTML = '\u{1F4C4} 下载 Word 文档';
            btnDocx.onclick = function() { downloadExport("docx", body, userText); };
            container.appendChild(btnDocx);
        }

        if (exportType === "pptx") {
            var btnPptx = document.createElement("button");
            btnPptx.className = "btn-export btn-export-pptx";
            btnPptx.innerHTML = '\u{1F4CA} 下载 PPT 课件';
            btnPptx.onclick = function() { downloadExport("pptx", body, userText); };
            container.appendChild(btnPptx);
        }

        if (exportType === "docx") {
            var btnPptx2 = document.createElement("button");
            btnPptx2.className = "btn-export btn-export-pptx";
            btnPptx2.innerHTML = '\u{1F4CA} 下载 PPT 课件';
            btnPptx2.onclick = function() { downloadExport("pptx", body, userText); };
            container.appendChild(btnPptx2);
        }

        body.appendChild(container);
        scrollToBottom();
    }

    async function downloadExport(format, body, userText) {
        var contentDiv = body.querySelector(".msg-content");
        var fullText = contentDiv ? contentDiv.innerText : "";

        if (!fullText.trim()) {
            alert("没有可导出的内容");
            return;
        }

        var btns = body.querySelectorAll(".btn-export");
        for (var i = 0; i < btns.length; i++) {
            btns[i].disabled = true;
            btns[i].textContent = "生成中...";
        }

        try {
            var title = userText.replace(/[\\/*?:"<>|]/g, "").substring(0, 30) || "教学文档";

            var resp = await fetch("/api/v1/export/" + format, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({content: fullText, title: title})
            });

            if (!resp.ok) {
                var err = await resp.json();
                throw new Error(err.error || "导出失败");
            }

            var blob = await resp.blob();
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = title + "." + format;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            alert("导出失败: " + e.message);
        } finally {
            for (var j = 0; j < btns.length; j++) {
                var originalText = format === "docx" ? '\u{1F4C4} 下载 Word 文档' : '\u{1F4CA} 下载 PPT 课件';
                btns[j].disabled = false;
                btns[j].textContent = originalText;
            }
        }
    }

    async function streamChat(userText, promptType) {
        var body = createAIBubble();
        var exportType = detectExportType(userText);

        if (abortController) { abortController.abort(); }
        abortController = new AbortController();

        if (stopBtn) {
            stopBtn.style.display = "flex";
            sendBtn.style.display = "none";
        }

        try {
            var response = await fetch("/api/v1/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    message: userText,
                    prompt_type: promptType || ""
                }),
                signal: abortController.signal
            });

            if (!response.ok) throw new Error("服务器错误 HTTP " + response.status);

            var reader = response.body.getReader();
            var decoder = new TextDecoder();
            var buffer = "";

            while (true) {
                var result = await reader.read();
                if (result.done) break;
                buffer += decoder.decode(result.value, {stream: true});
                var lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    if (line.substring(0, 6) !== "data: ") continue;
                    var jsonStr = line.substring(6).trim();
                    if (!jsonStr) continue;

                    try {
                        var event = JSON.parse(jsonStr);
                        if (event.type === "content") {
                            appendStreamChar(body, event.data);
                        } else if (event.type === "thinking") {
                            appendThinkingChar(body, event.data);
                        } else if (event.type === "done") {
                            finishMessage(body);
                            updateScrollNav();
                            if (exportType) {
                                setTimeout(function() {
                                    addExportButtons(body, exportType, userText);
                                }, 300);
                            }
                        }
                    } catch(e) {}
                }
            }
        } catch (err) {
            if (err.name !== "AbortError") {
                showError(body, "连接失败: " + err.message + "。请确认服务器正在运行。");
            } else {
                finishMessage(body);
            }
        } finally {
            abortController = null;
            if (stopBtn) {
                stopBtn.style.display = "none";
                sendBtn.style.display = "flex";
            }
        }
    }

    async function sendMessage() {
        var text = messageInput.value.trim();
        if (!text || isTyping) return;

        isTyping = true;
        userAtBottom = true;
        sendBtn.disabled = true;
        messageInput.value = "";
        autoResize();

        addUserMessage(text);
        await streamChat(text, null);

        isTyping = false;
        sendBtn.disabled = false;
        updateSendButton();
        messageInput.focus();
    }

    async function sendMessageByType(promptType, extraText) {
        var presets = {
            analysis: {
                text: "请帮我进行教学解析：选择一个你正在教或想教的知识点，我会为你详细分析教学重点、难点和突破方法。" + (extraText ? "\n\n具体需求：" + extraText : ""),
                type: "analysis"
            },
            suggestions: {
                text: "请帮我提供学习建议：告诉我你正在学习的科目和内容，我会为你制定个性化的学习计划和方法。" + (extraText ? "\n\n具体需求：" + extraText : ""),
                type: "suggestions"
            },
            explain: {
                text: "请帮我讲解一个知识点：告诉我你想学的概念或主题，我会用最简单的方式解释清楚。" + (extraText ? "\n\n具体需求：" + extraText : ""),
                type: "explain"
            },
            english: {
                text: "帮我学习高一英语：从词汇、语法、阅读、写作等方面为我制定学习内容。",
                type: "english"
            }
        };
        
        var preset = presets[promptType];
        if (!preset) return;
        
        isTyping = true;
        sendBtn.disabled = true;
        
        addUserMessage(preset.text);
        await streamChat(preset.text, preset.type);

        isTyping = false;
        sendBtn.disabled = false;
        updateSendButton();
        messageInput.focus();
    }

    if (stopBtn) {
        stopBtn.addEventListener("click", function() {
            if (abortController) {
                abortController.abort();
            }
        });
    }

    messageInput.addEventListener("input", function() { autoResize(); updateSendButton(); });
    messageInput.addEventListener("keydown", function(e) {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    sendBtn.addEventListener("click", sendMessage);
    messagesContainer.addEventListener("scroll", onScroll);

    var newChatBtn = document.getElementById("newChatBtn");
    if (newChatBtn) {
        newChatBtn.addEventListener("click", function() {
            if (confirm("确定要开始新会话吗？当前对话将被清空。")) {
                fetch("/api/v1/new-session", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({session_id: "default_session"})
                }).then(function() {
                    messagesContainer.innerHTML = createWelcomeHTML();
                    bindWelcomeInteractions();
                    updateScrollNav();
                });
            }
        });
    }

    function createWelcomeHTML() {
        return `
            <div class="welcome-section" id="welcomeSection">
                <div class="welcome-avatar">
                    <svg viewBox="0 0 48 48">
                        <ellipse cx="24" cy="24" rx="16" ry="14"/>
                        <circle cx="24" cy="20" r="6"/>
                        <circle cx="24" cy="19" r="2"/>
                        <line x1="24" y1="35" x2="18" y2="45"/>
                        <line x1="24" y1="35" x2="30" y2="45"/>
                        <line x1="24" y1="10" x2="24" y2="4"/>
                        <line x1="20" y1="11" x2="18" y2="5"/>
                        <line x1="28" y1="11" x2="30" y2="5"/>
                    </svg>
                </div>
                <div class="welcome-title">您好，困困</div>
                <div class="welcome-subtitle">我是您的全科 AI 教学助手，可以根据学科和学习情况，为您提供智能备课、知识讲解和学习建议。</div>
                <div class="feature-cards">
                    <div class="feature-card" data-prompt-type="analysis">
                        <div class="feature-icon-box icon-purple">📝</div>
                        <div class="feature-title">教学解析</div>
                        <div class="feature-desc">分析教学重点难点，提供突破方法和教学策略</div>
                        <div class="feature-tags">
                            <span class="feature-tag" data-tag-text="高一数学">高一数学</span>
                            <span class="feature-tag" data-tag-text="语文教案">语文教案</span>
                            <span class="feature-tag" data-tag-text="物理课件">物理课件</span>
                        </div>
                    </div>
                    <div class="feature-card" data-prompt-type="explain">
                        <div class="feature-icon-box icon-blue">💡</div>
                        <div class="feature-title">知识讲解</div>
                        <div class="feature-desc">由浅入深讲解知识点原理，帮助理解掌握</div>
                        <div class="feature-tags">
                            <span class="feature-tag" data-tag-text="数学解析">数学解析</span>
                            <span class="feature-tag" data-tag-text="语法分析">语法分析</span>
                            <span class="feature-tag" data-tag-text="化学原理">化学原理</span>
                        </div>
                    </div>
                    <div class="feature-card" data-prompt-type="suggestions">
                        <div class="feature-icon-box icon-green">🎯</div>
                        <div class="feature-title">学习建议</div>
                        <div class="feature-desc">个性化学习计划，智能答疑解惑，高效提升</div>
                        <div class="feature-tags">
                            <span class="feature-tag" data-tag-text="学习计划">学习计划</span>
                            <span class="feature-tag" data-tag-text="答疑解惑">答疑解惑</span>
                            <span class="feature-tag" data-tag-text="知识梳理">知识梳理</span>
                        </div>
                    </div>
                </div>
                
            </div>
        `;
    }

    function bindWelcomeInteractions() {
        var featureCards = messagesContainer.querySelectorAll(".feature-card");
        for (var i = 0; i < featureCards.length; i++) {
            featureCards[i].addEventListener("click", function(e) {
                if (e.target.classList.contains("feature-tag")) return;
                var promptType = this.getAttribute("data-prompt-type");
                if (promptType) {
                    sendMessageByType(promptType);
                }
            });
        }

        var featureTags = messagesContainer.querySelectorAll(".feature-tag");
        for (var j = 0; j < featureTags.length; j++) {
            featureTags[j].addEventListener("click", function(e) {
                e.stopPropagation();
                var tagText = this.getAttribute("data-tag-text");
                var card = this.closest(".feature-card");
                var promptType = card ? card.getAttribute("data-prompt-type") : "explain";
                var presetMap = {
                    "高一数学": { type: "analysis", text: "请帮我分析高一数学的教学重点和难点，提供突破方法。" },
                    "语文教案": { type: "analysis", text: "请帮我设计一份语文教案，包括教学目标、重难点和教学过程。" },
                    "物理课件": { type: "analysis", text: "请帮我制作物理课件的教学设计，包含重点难点分析。" },
                    "数学解析": { type: "explain", text: "请帮我详细解析数学知识点，从基础到进阶逐步讲解。" },
                    "语法分析": { type: "explain", text: "请帮我分析英语语法，用通俗易懂的方式讲解。" },
                    "化学原理": { type: "explain", text: "请帮我讲解化学原理，结合实例说明。" },
                    "学习计划": { type: "suggestions", text: "请帮我制定一个学习计划，帮助我系统学习相关知识。" },
                    "答疑解惑": { type: "suggestions", text: "请帮我解答学习中的疑问，提供详细的解释和思路。" },
                    "知识梳理": { type: "suggestions", text: "请帮我梳理知识体系，建立清晰的知识框架。" }
                };
                var preset = presetMap[tagText] || { type: promptType, text: "请帮我讲解关于" + tagText + "的内容。" };
                sendMessageByType(preset.type, preset.text);
            });
        }
    }

    checkHealth();
    createStars();
    createScrollNav();
    updateScrollNav();
    bindWelcomeInteractions();

    messageInput.focus();
    updateSendButton();
    autoResize();
})();
