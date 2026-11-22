/**
 * 87版《红楼梦》人物关系图谱 - 主交互应用逻辑
 */

document.addEventListener('DOMContentLoaded', () => {
  // 全局应用状态
  const state = {
    dataset: null,
    graph: null,
    pathFinder: null,
    currentPreset: 'core', // core, all, twelve, four_families, romance
    selectedClans: new Set(['rongguo', 'ningguo', 'shi', 'wang', 'xue', 'lin', 'servant', 'external']),
    selectedRelationTypes: new Set(['blood', 'marriage', 'love', 'master_servant', 'friendship', 'conflict']),
    selectedCharacter: null,
    theme: localStorage.getItem('honglou_theme') || 'dark'
  };

  // 应用主题
  applyTheme(state.theme);

  // 初始化图谱与数据
  initApp();

  async function initApp() {
    // 优先读取 window.HONGLOU_DATA (支持直接双击 file:// 零CORS运行)
    if (window.HONGLOU_DATA) {
      state.dataset = window.HONGLOU_DATA;
    } else {
      try {
        const resp = await fetch('data/honglou_data.json');
        state.dataset = await resp.json();
      } catch (err) {
        console.error('加载本地 JSON 数据失败，请检查网络或运行本地服务:', err);
        showToast('数据加载异常，请确认数据文件完整');
        return;
      }
    }

    // 实例化物理图谱与寻径器
    state.graph = new HonglouGraph('#graph-svg', {
      linkDistance: 220,
      linkStrength: 0.35,
      chargeStrength: -1600,
      onNodeClick: (node) => handleNodeSelect(node)
    });

    state.pathFinder = new RelationshipPathFinder(state.dataset.nodes, state.dataset.links);

    // 绑定小地图
    state.graph.bindMinimap('#minimap-canvas');

    // 灌入数据
    state.graph.setData(state.dataset);

    // 初始化界面交互组件
    setupUI();

    // 默认应用经典核心关系视图
    applyPreset('core');
  }

  // 界面交互事件绑定
  function setupUI() {
    // 布局模式切换 (侧边栏与浮动条双向同步)
    function updateLayoutMode(mode) {
      state.graph.setLayoutMode(mode);
      document.querySelectorAll('.layout-opt-btn[data-layout]').forEach(b => {
        b.classList.toggle('active', b.dataset.layout === mode);
      });
      document.getElementById('btn-layout-concentric')?.classList.toggle('active', mode === 'concentric');
      document.getElementById('btn-layout-clans')?.classList.toggle('active', mode === 'clans');
      document.getElementById('btn-layout-free')?.classList.toggle('active', mode === 'free');
      const modeNames = { concentric: '核心圈层层次', clans: '家族分区聚类', free: '自由弹性' };
      showToast(`已切换至「${modeNames[mode]}」布局`);
      setTimeout(() => state.graph.fitToView(900), 250);
    }

    document.querySelectorAll('.layout-opt-btn[data-layout]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        updateLayoutMode(e.currentTarget.dataset.layout);
      });
    });

    document.getElementById('btn-layout-concentric')?.addEventListener('click', () => updateLayoutMode('concentric'));
    document.getElementById('btn-layout-clans')?.addEventListener('click', () => updateLayoutMode('clans'));
    document.getElementById('btn-layout-free')?.addEventListener('click', () => updateLayoutMode('free'));

    // 关系文字显示策略切换
    document.querySelectorAll('.layout-opt-btn[data-labels]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.layout-opt-btn[data-labels]').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        const mode = e.currentTarget.dataset.labels;
        state.graph.setLabelDisplayMode(mode);
        showToast(mode === 'smart' ? '已开启智能精简模式（聚焦时展现文字，清爽无遮挡）' : '已开启全部显示所有连线文字');
      });
    });

    // 预设视图切换
    document.querySelectorAll('.preset-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        const preset = e.currentTarget.dataset.preset;
        applyPreset(preset);
      });
    });

    // 侧边栏折叠与展开
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarClose = document.getElementById('sidebar-close');

    sidebarToggle?.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      sidebarToggle.style.display = sidebar.classList.contains('collapsed') ? 'flex' : 'none';
    });

    sidebarClose?.addEventListener('click', () => {
      sidebar.classList.add('collapsed');
      sidebarToggle.style.display = 'flex';
    });

    // 侧边栏家族筛选标签
    renderClanFilters();

    // 侧边栏关系类型筛选标签
    renderRelationFilters();

    // 物理参数滑块
    setupPhysicsSliders();

    // 搜索输入与自动补全
    setupSearch();

    // 右侧生平手卷抽屉关闭
    document.getElementById('drawer-close')?.addEventListener('click', () => {
      closeDrawer();
      state.graph.clearSelection();
    });

    // 网站品牌徽标点击：全景自适应居中漫游
    document.querySelector('.brand-logo')?.addEventListener('click', () => {
      state.graph.fitToView(850);
      showToast('视角已漫游重置居中');
    });

    // 浮动工具栏按钮
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => state.graph.zoomIn());
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => state.graph.zoomOut());
    document.getElementById('btn-fit-view')?.addEventListener('click', () => state.graph.fitToView());
    document.getElementById('btn-toggle-play')?.addEventListener('click', function() {
      const isRunning = state.graph.toggleSimulation();
      this.classList.toggle('active', !isRunning);
      this.innerHTML = isRunning ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>' : '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
      showToast(isRunning ? '物理模拟已恢复' : '物理模拟已暂停');
    });

    document.getElementById('btn-unlock-all')?.addEventListener('click', () => {
      state.graph.unlockAllNodes();
      showToast('已释放全部固定节点');
    });

    // 主题切换
    document.getElementById('btn-theme-toggle')?.addEventListener('click', () => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('honglou_theme', state.theme);
      applyTheme(state.theme);
      showToast(`已切换至${state.theme === 'dark' ? '墨玉深色' : '素绢宣纸'}主题`);
    });

    // 模态弹窗相关
    setupModals();
  }

  // 渲染家族标签筛选器
  function renderClanFilters() {
    const container = document.getElementById('clan-filter-tags');
    if (!container) return;

    container.innerHTML = '';
    state.dataset.clans.forEach(clan => {
      const tag = document.createElement('div');
      tag.className = 'filter-tag active';
      tag.dataset.clan = clan.id;
      tag.innerHTML = `<span class="tag-dot" style="background: ${clan.color};"></span>${clan.name}`;

      tag.addEventListener('click', () => {
        tag.classList.toggle('active');
        if (state.selectedClans.has(clan.id)) {
          state.selectedClans.delete(clan.id);
        } else {
          state.selectedClans.add(clan.id);
        }
        applyCurrentFilters();
      });

      container.appendChild(tag);
    });
  }

  // 渲染关系类型筛选器
  function renderRelationFilters() {
    const container = document.getElementById('relation-filter-tags');
    if (!container) return;

    container.innerHTML = '';
    state.dataset.relationTypes.forEach(rel => {
      const tag = document.createElement('div');
      tag.className = 'filter-tag active';
      tag.dataset.type = rel.id;
      tag.innerHTML = `<span class="tag-dot" style="background: ${rel.color};"></span>${rel.name}`;

      tag.addEventListener('click', () => {
        tag.classList.toggle('active');
        if (state.selectedRelationTypes.has(rel.id)) {
          state.selectedRelationTypes.delete(rel.id);
        } else {
          state.selectedRelationTypes.add(rel.id);
        }
        applyCurrentFilters();
      });

      container.appendChild(tag);
    });
  }

  // 物理参数滑块调整
  function setupPhysicsSliders() {
    const distSlider = document.getElementById('slider-link-dist');
    const distVal = document.getElementById('val-link-dist');
    distSlider?.addEventListener('input', (e) => {
      const val = +e.target.value;
      if (distVal) distVal.textContent = val;
      state.graph.updateForces({ linkDistance: val });
    });

    const strengthSlider = document.getElementById('slider-tension');
    const strengthVal = document.getElementById('val-tension');
    strengthSlider?.addEventListener('input', (e) => {
      const val = +e.target.value;
      if (strengthVal) strengthVal.textContent = val;
      state.graph.updateForces({ linkStrength: val / 100 });
    });

    const chargeSlider = document.getElementById('slider-charge');
    const chargeVal = document.getElementById('val-charge');
    chargeSlider?.addEventListener('input', (e) => {
      const val = +e.target.value;
      if (chargeVal) chargeVal.textContent = val;
      state.graph.updateForces({ chargeStrength: -val });
    });
  }

  // 预设视图策略
  function applyPreset(presetKey) {
    state.currentPreset = presetKey;

    const twelveLadies = new Set([
      '贾宝玉', '林黛玉', '薛宝钗', '王熙凤', '贾元春', '贾探春', 
      '史湘云', '妙玉', '贾迎春', '贾惜春', '李纨', '贾巧姐', '秦可卿'
    ]);

    const fourClans = new Set(['rongguo', 'ningguo', 'shi', 'wang', 'xue']);

    switch (presetKey) {
      case 'core': // 经典核心 (前35位核心人物)
        state.graph.filterData(
          d => d.importance >= 3 || twelveLadies.has(d.name) || ['贾母', '贾政', '王夫人', '贾琏', '晴雯', '袭人', '紫鹃', '平儿', '刘姥姥'].includes(d.name),
          l => true
        );
        break;

      case 'all': // 全景宗族 (全部123位角色与187条关系链)
        state.graph.filterData(d => true, l => true);
        break;

      case 'twelve': // 金陵十二钗正册专场
        state.graph.filterData(d => twelveLadies.has(d.name), l => true);
        break;

      case 'four_families': // 四大家族聚焦 (贾、史、王、薛)
        state.graph.filterData(d => fourClans.has(d.clan), l => true);
        break;

      case 'romance': // 大观园情缘谱 (木石前盟、金玉良缘、知己深情)
        state.graph.filterData(
          d => true,
          l => l.type === 'love' || l.type === 'marriage' || ['木石前盟', '金玉良缘', '喜欢', '知己', '夫妻'].some(k => l.relation.includes(k))
        );
        break;
    }

    setTimeout(() => {
      state.graph.fitToView(900);
    }, 200);
  }

  // 应用侧边栏标签过滤
  function applyCurrentFilters() {
    state.graph.filterData(
      d => state.selectedClans.has(d.clan),
      l => state.selectedRelationTypes.has(l.type)
    );
  }

  // 搜索功能实现
  function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const searchDropdown = document.getElementById('search-dropdown');

    if (!searchInput || !searchDropdown) return;

    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      if (!q) {
        searchDropdown.style.display = 'none';
        return;
      }

      const matches = state.dataset.nodes.filter(n => {
        return n.name.toLowerCase().includes(q) ||
               (n.actor && n.actor.toLowerCase().includes(q)) ||
               (n.identity && n.identity.toLowerCase().includes(q)) ||
               (n.residence && n.residence.toLowerCase().includes(q));
      }).slice(0, 10);

      if (matches.length === 0) {
        searchDropdown.innerHTML = `<div style="padding: 10px; font-size: 12px; color: var(--text-muted); text-align: center;">未找到匹配人物</div>`;
        searchDropdown.style.display = 'block';
        return;
      }

      searchDropdown.innerHTML = matches.map(m => `
        <div class="search-item" data-id="${m.id}">
          <img class="search-item-avatar" src="${m.avatar}" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'30\\' height=\\'30\\'><rect width=\\'30\\' height=\\'30\\' fill=\\'%23b91c1c\\'/></svg>'">
          <div>
            <div class="search-item-name">${m.name}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${m.actor ? `${m.actor} 饰 · ` : ''}${m.clanName}</div>
          </div>
          <div class="search-item-sub">${m.residence !== '—' ? m.residence : m.identity}</div>
        </div>
      `).join('');

      searchDropdown.style.display = 'block';
    });

    searchDropdown.addEventListener('click', (e) => {
      const item = e.target.closest('.search-item');
      if (item) {
        const charId = item.dataset.id;
        state.graph.flyToNode(charId);
        searchDropdown.style.display = 'none';
        searchInput.value = '';
      }
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        searchDropdown.style.display = 'none';
      }
    });
  }

  // 选中节点展开生平手卷抽屉
  function handleNodeSelect(node) {
    if (!node) {
      closeDrawer();
      return;
    }

    state.selectedCharacter = node;
    const drawer = document.getElementById('profile-drawer');
    if (!drawer) return;

    // 填充抽屉内容
    document.getElementById('drawer-avatar').src = node.avatar;
    document.getElementById('drawer-actor').textContent = node.actor ? `${node.actor} 饰` : '87版电视剧角色';
    document.getElementById('drawer-name').textContent = node.name;
    document.getElementById('drawer-clan-badge').textContent = node.clanName;
    document.getElementById('drawer-identity').textContent = node.identity || '—';
    document.getElementById('drawer-residence').textContent = node.residence || '—';
    document.getElementById('drawer-generation').textContent = node.generation || '—';

    // 判词引用
    const quoteEl = document.getElementById('drawer-judgment');
    if (node.judgment) {
      quoteEl.textContent = node.judgment;
      quoteEl.parentElement.style.display = 'block';
    } else {
      quoteEl.parentElement.style.display = 'none';
    }

    // 生平介绍
    document.getElementById('drawer-desc').textContent = node.description || '暂无详细生平介绍。';

    // 人物直接关系列表
    const relationsList = document.getElementById('drawer-relations-list');
    relationsList.innerHTML = '';

    const directRelations = state.dataset.links.filter(l => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      return s === node.id || t === node.id;
    });

    if (directRelations.length === 0) {
      relationsList.innerHTML = `<div style="font-size: 12px; color: var(--text-muted);">暂无记录关联关系</div>`;
    } else {
      directRelations.forEach(r => {
        const s = typeof r.source === 'object' ? r.source.id : r.source;
        const t = typeof r.target === 'object' ? r.target.id : r.target;
        const targetId = s === node.id ? t : s;
        const targetChar = state.dataset.nodes.find(n => n.id === targetId);

        if (targetChar) {
          const item = document.createElement('div');
          item.className = 'relation-item';
          item.innerHTML = `
            <img class="rel-target-avatar" src="${targetChar.avatar}" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'30\\' height=\\'30\\'><rect width=\\'30\\' height=\\'30\\' fill=\\'%23b91c1c\\'/></svg>'">
            <div class="rel-info">
              <span class="rel-target-name">${targetChar.name}</span>
              <span class="rel-tag-badge">${r.relation}</span>
            </div>
            <span style="font-size: 11px; color: var(--accent-gold);">${r.type === 'love' ? '❤️' : (r.type === 'blood' ? '🩸' : '🔗')}</span>
          `;

          // 点击关系卡片，画布平滑飞往目标人物
          item.addEventListener('click', () => {
            state.graph.flyToNode(targetChar.id);
          });

          relationsList.appendChild(item);
        }
      });
    }

    drawer.classList.add('open');
  }

  function closeDrawer() {
    const drawer = document.getElementById('profile-drawer');
    drawer?.classList.remove('open');
    state.selectedCharacter = null;
  }

  // 模态弹窗系统：扩充数据、关系寻径、关于
  function setupModals() {
    // 打开扩充数据弹窗
    document.getElementById('btn-add-data')?.addEventListener('click', () => {
      openModal('modal-expand-data');
      populateCharacterSelects();
    });

    // 打开关系寻径弹窗
    document.getElementById('btn-path-finder')?.addEventListener('click', () => {
      openModal('modal-path-finder');
      populatePathFinderSelects();
    });

    // 导出高清图
    document.getElementById('btn-export-img')?.addEventListener('click', () => {
      exportGraphImage();
    });

    // 弹窗关闭按钮
    document.querySelectorAll('.modal-close-btn, .modal-cancel-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const overlay = e.target.closest('.modal-overlay');
        overlay?.classList.remove('active');
      });
    });

    // 模态标签页切换
    document.querySelectorAll('.modal-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const container = e.target.closest('.modal-box');
        container.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
        container.querySelectorAll('.modal-tab-pane').forEach(p => p.style.display = 'none');

        e.currentTarget.classList.add('active');
        const tabId = e.currentTarget.dataset.tab;
        const targetPane = document.getElementById(tabId);
        if (targetPane) targetPane.style.display = 'flex';
      });
    });

    // 新增人物表单提交
    document.getElementById('form-add-character')?.addEventListener('submit', (e) => {
      e.preventDefault();
      addNewCharacter();
    });

    // 新增关系表单提交
    document.getElementById('form-add-relation')?.addEventListener('submit', (e) => {
      e.preventDefault();
      addNewRelationship();
    });

    // 关系寻径表单提交
    document.getElementById('form-find-path')?.addEventListener('submit', (e) => {
      e.preventDefault();
      runPathSearch();
    });

    // JSON 导出按钮
    document.getElementById('btn-download-json')?.addEventListener('click', () => {
      downloadDatasetJSON();
    });

    // JSON 导入文件监听
    document.getElementById('input-import-json')?.addEventListener('change', (e) => {
      handleJSONFileImport(e);
    });
  }

  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
  }

  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  }

  // 填充下拉选项
  function populateCharacterSelects() {
    const sourceSelect = document.getElementById('rel-source-select');
    const targetSelect = document.getElementById('rel-target-select');
    if (!sourceSelect || !targetSelect) return;

    const optionsHtml = state.dataset.nodes
      .sort((a, b) => a.name.localeCompare(b.name, 'zh'))
      .map(n => `<option value="${n.id}">${n.name} (${n.clanName})</option>`)
      .join('');

    sourceSelect.innerHTML = `<option value="">-- 请选择起始人物 --</option>` + optionsHtml;
    targetSelect.innerHTML = `<option value="">-- 请选择目标人物 --</option>` + optionsHtml;
  }

  function populatePathFinderSelects() {
    const sourceSelect = document.getElementById('path-source-select');
    const targetSelect = document.getElementById('path-target-select');
    if (!sourceSelect || !targetSelect) return;

    const optionsHtml = state.dataset.nodes
      .sort((a, b) => a.name.localeCompare(b.name, 'zh'))
      .map(n => `<option value="${n.id}">${n.name} (${n.clanName})</option>`)
      .join('');

    sourceSelect.innerHTML = optionsHtml;
    targetSelect.innerHTML = optionsHtml;

    // 默认预设：贾宝玉 与 林黛玉
    sourceSelect.value = '贾宝玉';
    targetSelect.value = '林黛玉';
  }

  // 新增角色入库
  function addNewCharacter() {
    const name = document.getElementById('new-char-name').value.trim();
    if (!name) {
      showToast('请输入人物姓名');
      return;
    }

    if (state.dataset.nodes.some(n => n.id === name || n.name === name)) {
      showToast('该人物已存在');
      return;
    }

    const clan = document.getElementById('new-char-clan').value;
    const clanInfo = state.dataset.clans.find(c => c.id === clan) || state.dataset.clans[0];
    const actor = document.getElementById('new-char-actor').value.trim();
    const identity = document.getElementById('new-char-identity').value.trim() || `${clanInfo.name}人物`;
    const residence = document.getElementById('new-char-residence').value.trim() || '—';
    const avatar = document.getElementById('new-char-avatar').value.trim() || `assets/avatars/${name}.jpg`;
    const judgment = document.getElementById('new-char-judgment').value.trim();
    const desc = document.getElementById('new-char-desc').value.trim() || `${name}，87版电视剧《红楼梦》人物。`;
    const importance = +document.getElementById('new-char-importance').value || 3;

    const newChar = {
      id: name,
      name: name,
      avatar: avatar,
      actor: actor,
      gender: '女',
      clan: clan,
      clanName: clanInfo.name,
      identity: identity,
      generation: '—',
      residence: residence,
      judgment: judgment,
      importance: importance,
      description: desc,
      tags: [clanInfo.name, '用户新增']
    };

    // 压入全局数据集
    state.dataset.nodes.push(newChar);
    state.pathFinder.update(state.dataset.nodes, state.dataset.links);

    // 刷新图谱
    state.graph.setData(state.dataset);
    state.graph.flyToNode(name);

    closeModal('modal-expand-data');
    showToast(`成功新增人物「${name}」！`);
  }

  // 新增关系入库
  function addNewRelationship() {
    const source = document.getElementById('rel-source-select').value;
    const target = document.getElementById('rel-target-select').value;
    const relation = document.getElementById('new-rel-name').value.trim();
    const type = document.getElementById('new-rel-type').value;
    const desc = document.getElementById('new-rel-desc').value.trim() || `${source} 与 ${target} 的${relation}关联。`;

    if (!source || !target || !relation) {
      showToast('请完整选择人物并填写关系名称');
      return;
    }

    if (source === target) {
      showToast('起始人物与目标人物不能相同');
      return;
    }

    const newLink = {
      source: source,
      target: target,
      relation: relation,
      type: type,
      desc: desc
    };

    state.dataset.links.push(newLink);
    state.pathFinder.update(state.dataset.nodes, state.dataset.links);

    // 刷新图谱
    state.graph.setData(state.dataset);

    closeModal('modal-expand-data');
    showToast(`成功新增关系「${source} --[${relation}]--> ${target}」！`);
  }

  // 执行两人物之间的最短关系寻径 (BFS)
  function runPathSearch() {
    const sId = document.getElementById('path-source-select').value;
    const tId = document.getElementById('path-target-select').value;

    if (!sId || !tId) {
      showToast('请选择两位人物');
      return;
    }

    if (sId === tId) {
      showToast('请选择两个不同的人物进行关系探寻');
      return;
    }

    const result = state.pathFinder.findShortestPath(sId, tId);
    const resultBox = document.getElementById('path-result-box');

    if (!result) {
      resultBox.innerHTML = `
        <div style="padding: 14px; text-align: center; color: var(--accent-vermilion); font-size: 13px;">
          未在当前谱系中找到两者的直接连通路径
        </div>
      `;
      resultBox.style.display = 'block';
      return;
    }

    // 渲染路径阶梯
    let html = `
      <div style="font-size: 12px; color: var(--accent-gold); font-weight: 600; margin-bottom: 8px;">
        ✨ 找到关系链（共经过 ${result.length} 度关系）：
      </div>
      <div style="display: flex; flex-direction: column; gap: 6px;">
    `;

    result.steps.forEach((step, idx) => {
      html += `
        <div style="display: flex; align-items: center; gap: 8px; font-size: 13px; background: var(--bg-tertiary); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
          <span style="font-weight: bold; color: var(--text-primary);">${step.from}</span>
          <span style="font-size: 11px; padding: 2px 8px; border-radius: 4px; background: rgba(212,175,55,0.15); color: var(--accent-gold);">${step.relation}</span>
          <span style="color: var(--text-muted);">➔</span>
          <span style="font-weight: bold; color: var(--text-primary);">${step.to}</span>
        </div>
      `;
    });

    html += `</div>`;
    resultBox.innerHTML = html;
    resultBox.style.display = 'block';

    // 在图谱中高亮整条路径
    const edgeKeys = result.steps.map(s => `${s.from}->${s.to}`);
    state.graph.highlightPath(result.nodes, edgeKeys);

    closeModal('modal-path-finder');
    showToast(`已在画布中高亮显示「${sId}」至「${tId}」的关联路径！`);
  }

  // 导出 JSON 数据文件
  function downloadDatasetJSON() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state.dataset, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `honglou_data_export_${new Date().toISOString().slice(0, 10)}.json`);
    dlAnchor.click();
    showToast('已成功导出红楼梦关系数据 JSON 文件！');
  }

  // 导入自定义 JSON
  function handleJSONFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target.result);
        if (!imported.nodes || !imported.links) {
          throw new Error('JSON 格式必须包含 nodes 与 links 数组');
        }
        state.dataset = imported;
        state.graph.setData(state.dataset);
        state.pathFinder.update(state.dataset.nodes, state.dataset.links);
        closeModal('modal-expand-data');
        showToast(`导入成功！载入 ${imported.nodes.length} 位人物与 ${imported.links.length} 条关系。`);
      } catch (err) {
        alert('导入 JSON 文件失败，请检查文件格式是否有效: ' + err.message);
      }
    };
    reader.readAsText(file);
  }

  // 导出高清图谱图片 (PNG)
  function exportGraphImage() {
    showToast('正在生成高清图谱图片...');
    const svgEl = document.getElementById('graph-svg');
    const svgData = new XMLSerializer().serializeToString(svgEl);
    const canvas = document.createElement('canvas');
    const rect = svgEl.getBoundingClientRect();
    const scale = 2; // 2x 超高清
    canvas.width = rect.width * scale;
    canvas.height = rect.height * scale;
    const ctx = canvas.getContext('2d');

    const img = new Image();
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      // 绘制背景底色
      ctx.fillStyle = state.theme === 'dark' ? '#12141a' : '#f8f6f0';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);

      const a = document.createElement('a');
      a.download = `87版红楼梦人物关系图_${new Date().toISOString().slice(0, 10)}.png`;
      a.href = canvas.toDataURL('image/png');
      a.click();
      showToast('高清图谱已成功保存！');
    };
    img.src = url;
  }

  // 主题切换辅助
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  // 轻量提示条
  function showToast(msg) {
    let toast = document.getElementById('toast-notice');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast-notice';
      toast.className = 'toast-notice';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }
});
