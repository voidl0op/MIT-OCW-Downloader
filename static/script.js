const btn = document.getElementById('download-btn')
const browseBtn = document.getElementById('browse-btn')
const toggleBtn = document.getElementById('toggle-btn')
const logBox = document.getElementById('log-box')
const fill = document.getElementById('prog-fill')
const progLabel = document.getElementById('prog-label')
const progPct = document.getElementById('prog-pct')
const statusBadge = document.getElementById('status-badge')

browseBtn.addEventListener('click', async () => {
    const res = await fetch('/browse')
    const data = await res.json()
    if (data.folder) {
        document.getElementById('folder-input').value = data.folder
    }
})

toggleBtn.addEventListener('click', () => {
    const hidden = logBox.style.display === 'none'
    logBox.style.display = hidden ? 'block' : 'none'
    toggleBtn.textContent = hidden ? 'Hide logs' : 'Show logs'
})

function setStatus(s) {
    statusBadge.className = 'status-badge status-' + s
    statusBadge.textContent = s === 'idle' ? 'Idle' : s === 'running' ? 'Running' : 'Done'
}

function appendLog(msg, type) {
    const placeholder = logBox.querySelector('.log-placeholder')
    if (placeholder) placeholder.remove()
    const p = document.createElement('p')
    p.className = 'log-line' + (type ? ' ' + type : '')
    p.textContent = msg
    logBox.appendChild(p)
    logBox.scrollTop = logBox.scrollHeight
}

function setProgress(pct, label) {
    fill.style.width = Math.min(pct, 100) + '%'
    progPct.textContent = Math.min(pct, 100) + '%'
    progLabel.textContent = label
}

btn.addEventListener('click', () => {
    const url = document.getElementById('url-input').value.trim()
    const folder = document.getElementById('folder-input').value.trim()

    if (!url) { alert('Please enter a course URL.'); return }
    if (!folder) { alert('Please select a download folder.'); return }

    logBox.innerHTML = '<p class="log-placeholder">Logs will appear here once you start a download.</p>'
    setProgress(0, 'Starting...')
    setStatus('running')
    btn.disabled = true
    browseBtn.disabled = true

    const source = new EventSource('/download?url=' + encodeURIComponent(url) + '&folder=' + encodeURIComponent(folder))

    source.onmessage = function (e) {
        const msg = e.data
        const isError = msg.toLowerCase().includes('error')
        appendLog(msg, isError ? 'error' : msg.includes('Saved') ? 'success' : '')

        const foundMatch = msg.match(/Found (\d+) resource/)
        if (foundMatch) setProgress(5, 'Found ' + foundMatch[1] + ' files')

        const progMatch = msg.match(/\[(\d+)\/(\d+)\]/)
        if (progMatch) {
            const cur = parseInt(progMatch[1])
            const tot = parseInt(progMatch[2])
            setProgress(Math.round((cur / tot) * 100), 'Downloading file ' + cur + ' of ' + tot)
        }

        if (msg.includes('Finished.')) {
            setProgress(100, 'All done!')
            setStatus('done')
            btn.disabled = false
            browseBtn.disabled = false
            source.close()
        }
    }

    source.onerror = () => {
        appendLog('Stream ended.')
        setStatus('idle')
        btn.disabled = false
        browseBtn.disabled = false
        source.close()
    }
})