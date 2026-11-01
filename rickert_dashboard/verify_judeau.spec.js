const { test, expect } = require('@playwright/test');
const path = require('path');

test('Verify Dashboard Layout by Judeau', async ({ page }) => {
    const filePath = 'file://' + path.resolve('C:/Users/xanth/Dropbox/個人請負/品川区テニス連盟/hp/docs/rickert_dashboard/dashboard.html');
    await page.goto(filePath);

    await page.evaluate(() => {
        if (window.RICKERT_DATA) {
            window.RICKERT_DATA.gh_actions = {
                status: 'in_progress',
                html_url: 'https://github.com/example/runs/1',
                conclusion: null
            };
            const ghEl = document.getElementById('gh-status');
            ghEl.style.display = 'flex';
            ghEl.className = 'gh-status gh-working';
            ghEl.innerHTML = '<i class=\"fa-solid fa-truck-ramp-box\"></i><span>輸送中...</span>';
        }
    });

    await page.waitForTimeout(1000);

    const ghStatus = page.locator('#gh-status');
    const syncStatus = page.locator('#sync-status');
    
    const ghBox = await ghStatus.boundingBox();
    const syncBox = await syncStatus.boundingBox();
    
    console.log('GH Status Box:', JSON.stringify(ghBox));
    console.log('Sync Status Box:', JSON.stringify(syncBox));

    if (ghBox && syncBox) {
        const diff = Math.abs((ghBox.y + ghBox.height / 2) - (syncBox.y + syncBox.height / 2));
        console.log('Vertical alignment diff:', diff);
        expect(diff).toBeLessThan(10); 
    }

    const main = page.locator('main');
    const gridTemplate = await main.evaluate(el => window.getComputedStyle(el).gridTemplateColumns);
    console.log('Grid Template Columns:', gridTemplate);
    const columns = gridTemplate.split(' ');
    expect(columns.length).toBe(3);
    expect(columns[0]).toBe('320px');
    expect(columns[2]).toBe('380px');

    const chatArea = page.locator('#chat-area');
    
    await page.evaluate(() => {
        const container = document.getElementById('chat-area');
        for (let i = 0; i < 50; i++) {
            const div = document.createElement('div');
            div.className = 'message-row sender-agent';
            div.innerHTML = '<div class=\"message-avatar\"><img src=\"assets/avatars/judeau.png\"></div>' +
                            '<div class=\"message-wrapper\">' +
                            '<div class=\"message-body\">偵察中の報告その' + i + '。異常なし。</div>' +
                            '<div class=\"message-info\">Judeau ? 02:00</div>' +
                            '</div>';
            container.appendChild(div);
        }
    });

    const isScrollable = await chatArea.evaluate(el => el.scrollHeight > el.clientHeight);
    console.log('Chat Area is scrollable:', isScrollable);
    expect(isScrollable).toBe(true);

    await page.screenshot({ path: 'C:/Users/xanth/dashboard_judeau_verify.png', fullPage: true });
});
