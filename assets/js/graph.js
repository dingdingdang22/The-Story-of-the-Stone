/**
 * 87版《红楼梦》人物关系图谱 - 核心物理图谱引擎 (D3.js Force Simulation)
 * 升级版：解决过于密集、层次圈层布局、移除头像文字、选中放大、拖拽保持位置不自动复位
 */

class HonglouGraph {
  constructor(svgSelector, options = {}) {
    this.svg = d3.select(svgSelector);
    this.options = Object.assign({
      linkDistance: 220,      // 大幅增加连接线长度，彻底拉开间距
      linkStrength: 0.35,     // 柔和弹性
      chargeStrength: -1600,  // 大幅增强排斥力，解决密集拥挤
      collidePadding: 40,     // 碰撞缓冲，保证节点间开阔距离
      onNodeClick: null,
      onNodeHover: null
    }, options);

    this.container = this.svg.append('g').attr('class', 'graph-container');
    this.defs = this.svg.append('defs');
    
    // 图元分层分组 (保证层次渲染顺序)
    this.linkGroup = this.container.append('g').attr('class', 'links-group');
    this.linkLabelGroup = this.container.append('g').attr('class', 'link-labels-group');
    this.nodeGroup = this.container.append('g').attr('class', 'nodes-group');

    // 数据状态
    this.allNodes = [];
    this.allLinks = [];
    this.activeNodes = [];
    this.activeLinks = [];
    this.nodeMap = new Map();

    // 交互状态
    this.selectedNode = null;
    this.hoveredNode = null;
    this.pinnedNodes = new Set();
    this.isSimulationRunning = true;
    this.layoutMode = 'concentric'; // 'concentric' (核心圈层), 'clans' (家族分区), 'free' (自由弹性)
    this.labelDisplayMode = 'smart'; // 'smart' (智能精简), 'all' (全部显示)

    // 缩放控制器
    this.zoom = d3.zoom()
      .scaleExtent([0.1, 4.0])
      .on('zoom', (event) => {
        this.container.attr('transform', event.transform);
        this.updateMinimap();
      });

    this.svg.call(this.zoom)
      .on('dblclick.zoom', null) // 禁用默认双击缩放，用于双击固定/释放节点
      .on('click', (event) => {
        if (event.target.tagName === 'svg' || event.target.id === 'graph-svg') {
          this.clearSelection();
        }
      });

    this.initMarkers();
    this.initSimulation();

    window.addEventListener('resize', () => this.handleResize());
  }

  initMarkers() {
    const arrowTypes = [
      { id: 'arrow-blood', color: '#e53e3e' },
      { id: 'arrow-marriage', color: '#d53f8c' },
      { id: 'arrow-love', color: '#ed64a6' },
      { id: 'arrow-master_servant', color: '#3182ce' },
      { id: 'arrow-friendship', color: '#38a169' },
      { id: 'arrow-conflict', color: '#718096' },
      { id: 'arrow-default', color: '#b3aba0' }
    ];

    arrowTypes.forEach(t => {
      this.defs.append('marker')
        .attr('id', t.id)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 9)
        .attr('refY', 0)
        .attr('markerWidth', 6.5)
        .attr('markerHeight', 6.5)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-4L9,0L0,4')
        .attr('fill', t.color);
    });

    // 柔光高亮滤镜
    const filter = this.defs.append('filter')
      .attr('id', 'glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    filter.append('feGaussianBlur')
      .attr('stdDeviation', '6')
      .attr('result', 'coloredBlur');

    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');
  }

  initSimulation() {
    const { width, height } = this.getDimensions();
    const cx = width / 2;
    const cy = height / 2;

    this.simulation = d3.forceSimulation()
      .alphaDecay(0.028)
      .force('link', d3.forceLink().id(d => d.id)
        .distance(d => this.getLinkDistance(d))
        .strength(this.options.linkStrength))
      .force('charge', d3.forceManyBody().strength(d => this.getChargeStrength(d)))
      .force('collide', d3.forceCollide().radius(d => this.getNodeRadius(d) + this.options.collidePadding).iterations(2))
      .force('center', d3.forceCenter(cx, cy).strength(0.03))
      .on('tick', () => this.tick());

    this.applyLayoutForces();
  }

  // 层次化圈层半径定义
  getTierRadius(tier) {
    switch (tier) {
      case 1: return 140;  // 核心中枢圈：贾母、宝黛钗凤、贾政、王夫人等
      case 2: return 380;  // 第二圈：金陵十二钗正副册群芳与近支宗室
      case 3: return 680;  // 第三圈：贴身大丫鬟、侍从与大观园知己
      case 4: default: return 1020; // 外围圈：外戚故旧、世交王侯、方外仙师
    }
  }

  getLinkDistance(link) {
    const s = typeof link.source === 'object' ? link.source : this.nodeMap.get(link.source);
    const t = typeof link.target === 'object' ? link.target : this.nodeMap.get(link.target);
    if (!s || !t) return this.options.linkDistance;

    // 核心层之间的纽带保持优雅间距，越往外越开阔
    if (s.tier === 1 && t.tier === 1) return 180;
    if (s.tier <= 2 && t.tier <= 2) return 220;
    return 260;
  }

  getChargeStrength(d) {
    // 核心大节点拥有更强排斥力，确保外围节点呈环状有序排列
    if (d.tier === 1) return -2600;
    if (d.tier === 2) return -1800;
    if (d.tier === 3) return -1400;
    return -1000;
  }

  // 应用不同布局模式下的专有向心/分区力
  applyLayoutForces() {
    const { width, height } = this.getDimensions();
    const cx = width / 2;
    const cy = height / 2;

    if (this.layoutMode === 'concentric') {
      // 核心圈层布局：按四大层级同心圆发散排列
      this.simulation
        .force('radial', d3.forceRadial(d => this.getTierRadius(d.tier || 4), cx, cy).strength(0.72))
        .force('clanX', null)
        .force('clanY', null);
    } else if (this.layoutMode === 'clans') {
      // 家族分区布局：各大宗族各自聚簇
      const clanFoci = {
        rongguo:  { x: cx - 450, y: cy + 120 }, // 荣国府（西南）
        ningguo:  { x: cx - 450, y: cy - 350 }, // 宁国府（西北）
        xue:      { x: cx + 450, y: cy - 250 }, // 薛家（东北）
        shi:      { x: cx + 150, y: cy - 450 }, // 史家（正北偏东）
        wang:     { x: cx - 150, y: cy - 450 }, // 王家（正北偏西）
        lin:      { x: cx - 150, y: cy + 450 }, // 林家（正南偏西）
        servant:  { x: cx + 400, y: cy + 250 }, // 大观园侍从（东南）
        external: { x: cx + 100, y: cy + 500 }  // 故旧方外（正南偏东）
      };

      this.simulation
        .force('radial', null)
        .force('clanX', d3.forceX(d => (clanFoci[d.clan] || { x: cx }).x).strength(0.45))
        .force('clanY', d3.forceY(d => (clanFoci[d.clan] || { y: cy }).y).strength(0.45));
    } else {
      // 自由弹性物理漫游
      this.simulation
        .force('radial', null)
        .force('clanX', null)
        .force('clanY', null);
    }

    this.simulation.alpha(0.6).restart();
  }

  setLayoutMode(mode) {
    if (this.layoutMode === mode) return;
    this.layoutMode = mode;
    this.applyLayoutForces();
  }

  setLabelDisplayMode(mode) {
    this.labelDisplayMode = mode;
    this.updateLabelVisibility();
  }

  getDimensions() {
    const rect = this.svg.node().getBoundingClientRect();
    return {
      width: rect.width || window.innerWidth,
      height: rect.height || (window.innerHeight - 64)
    };
  }

  handleResize() {
    const { width, height } = this.getDimensions();
    this.simulation.force('center', d3.forceCenter(width / 2, height / 2));
    this.applyLayoutForces();
    this.updateMinimap();
  }

  // 阶梯节点半径尺寸 (默认尺寸)
  getNodeRadius(d) {
    if (d.tier === 1) return 36;
    if (d.tier === 2) return 30;
    if (d.tier === 3) return 25;
    return 21;
  }

  // 选中或悬停时的放大半径 (需求3：鼠标选中头像变大)
  getEnlargedRadius(d) {
    return Math.max(58, Math.round(this.getNodeRadius(d) * 1.88));
  }

  getClanColor(clanId) {
    const clanColors = {
      rongguo: '#c53030', // 荣国府 - 绛红
      ningguo: '#9b2c2c', // 宁国府 - 枣红
      shi: '#c05621',     // 史家 - 琥珀金
      wang: '#b7791f',    // 王家 - 沉香
      xue: '#2c7a7b',     // 薛家 - 翡翠绿
      lin: '#2b6cb0',     // 林家 - 霁蓝
      servant: '#2f855a', // 丫鬟侍从 - 竹青
      external: '#6b46c1' // 故旧方外 - 绛紫
    };
    return clanColors[clanId] || '#d4af37';
  }

  getRelationColor(type) {
    const relColors = {
      blood: '#e53e3e',
      marriage: '#d53f8c',
      love: '#ed64a6',
      master_servant: '#3182ce',
      friendship: '#38a169',
      conflict: '#718096'
    };
    return relColors[type] || '#b3aba0';
  }

  // 灌入数据集
  setData(dataset) {
    this.dataset = dataset;
    this.allNodes = JSON.parse(JSON.stringify(dataset.nodes));
    this.allLinks = JSON.parse(JSON.stringify(dataset.links));

    this.nodeMap.clear();
    this.allNodes.forEach(n => this.nodeMap.set(n.id, n));

    this.filterData(() => true, () => true);
  }

  filterData(nodeFilter, linkFilter) {
    const filteredNodes = this.allNodes.filter(nodeFilter);
    const activeNodeIds = new Set(filteredNodes.map(n => n.id));

    const filteredLinks = this.allLinks.filter(link => {
      const s = typeof link.source === 'object' ? link.source.id : link.source;
      const t = typeof link.target === 'object' ? link.target.id : link.target;
      return activeNodeIds.has(s) && activeNodeIds.has(t) && linkFilter(link);
    });

    // 为多条连接计算弯曲曲率偏移
    const pairCount = new Map();
    filteredLinks.forEach(l => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      const key = s < t ? `${s}_${t}` : `${t}_${s}`;
      const count = pairCount.get(key) || 0;
      pairCount.set(key, count + 1);
      l.linkIndex = count;
    });

    filteredLinks.forEach(l => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      const key = s < t ? `${s}_${t}` : `${t}_${s}`;
      const total = pairCount.get(key);
      l.curvature = total > 1 ? (l.linkIndex - (total - 1) / 2) * 0.28 : 0;
    });

    this.activeNodes = filteredNodes;
    this.activeLinks = filteredLinks;

    this.render();
  }

  render() {
    this.updateAvatarPatterns();
    this.renderLinks();
    this.renderNodes();

    this.simulation.nodes(this.activeNodes);
    this.simulation.force('link').links(this.activeLinks);
    this.applyLayoutForces();
    this.simulation.alpha(0.85).restart();
  }

  /**
   * 需求2：头像上不要有文字！
   * 移除此前在 pattern 中覆盖在头像上的 text 元素，保证 87 版纯粹高清人脸展现
   */
  updateAvatarPatterns() {
    const patterns = this.defs.selectAll('pattern.avatar-pattern')
      .data(this.activeNodes, d => d.id);

    patterns.exit().remove();

    const patternEnter = patterns.enter()
      .append('pattern')
      .attr('class', 'avatar-pattern')
      .attr('id', d => `avatar-${d.id}`)
      .attr('width', 1)
      .attr('height', 1)
      .attr('patternContentUnits', 'objectBoundingBox');

    // 底层纯色背景（仅在图片加载失败或空缺时展现）
    patternEnter.append('rect')
      .attr('width', 1)
      .attr('height', 1)
      .attr('fill', d => this.getClanColor(d.clan));

    // 87 版角色剧照头像（不再叠加任何文字！）
    patternEnter.append('image')
      .attr('width', 1)
      .attr('height', 1)
      .attr('preserveAspectRatio', 'xMidYMid slice')
      .attr('href', d => d.avatar);
  }

  renderLinks() {
    const links = this.linkGroup.selectAll('path.graph-link')
      .data(this.activeLinks, d => `${d.source.id || d.source}_${d.target.id || d.target}_${d.relation}`);

    links.exit().remove();

    const linkEnter = links.enter()
      .append('path')
      .attr('class', 'graph-link')
      .attr('stroke', d => this.getRelationColor(d.type))
      .attr('stroke-width', d => d.type === 'love' ? 2.6 : 1.8)
      .attr('stroke-dasharray', d => d.type === 'love' ? '6,4' : (d.type === 'conflict' ? '3,3' : null))
      .attr('marker-end', d => `url(#arrow-${d.type || 'default'})`)
      .style('opacity', 0.28); // 默认轻盈半透明，降低背景线条干扰

    this.linkElements = linkEnter.merge(links);

    // 关系文本标签
    const labels = this.linkLabelGroup.selectAll('text.graph-link-label')
      .data(this.activeLinks, d => `${d.source.id || d.source}_${d.target.id || d.target}_${d.relation}`);

    labels.exit().remove();

    const labelEnter = labels.enter()
      .append('text')
      .attr('class', 'graph-link-label')
      .attr('text-anchor', 'middle')
      .attr('dy', '-4px')
      .text(d => d.relation);

    this.linkLabelElements = labelEnter.merge(labels);
    this.updateLabelVisibility();
  }

  // 关系文字智能精简可见度管理
  updateLabelVisibility() {
    if (!this.linkLabelElements) return;

    const focusNodeId = this.selectedNode ? this.selectedNode.id : (this.hoveredNode ? this.hoveredNode.id : null);

    if (focusNodeId) {
      // 当处于选中或悬停人物状态时：严格只显示与该人物直接相连的关系文字！其余一律100%彻底隐藏并消除DOM占用，坚决杜绝背景干扰！
      this.linkLabelElements
        .style('display', d => {
          const s = d.source.id || d.source;
          const t = d.target.id || d.target;
          return (s === focusNodeId || t === focusNodeId) ? 'block' : 'none';
        })
        .style('opacity', d => {
          const s = d.source.id || d.source;
          const t = d.target.id || d.target;
          return (s === focusNodeId || t === focusNodeId) ? 1.0 : 0;
        })
        .style('font-weight', '600')
        .style('font-size', '12px')
        .style('fill', '#ffffff');
      return;
    }

    // 未选中任何人物时：根据全局模式展现
    if (this.labelDisplayMode === 'all') {
      this.linkLabelElements
        .style('display', 'block')
        .style('opacity', 0.85)
        .style('font-weight', 'normal')
        .style('font-size', '11px')
        .style('fill', 'var(--text-secondary)');
    } else {
      // 智能精简模式：默认仅显示主线核心关系
      this.linkLabelElements
        .style('display', d => {
          if (['木石前盟', '金玉良缘', '结发夫妻', '祖孙至亲', '母子至亲'].some(k => d.relation.includes(k))) {
            return 'block';
          }
          return 'none';
        })
        .style('opacity', d => {
          if (['木石前盟', '金玉良缘', '结发夫妻', '祖孙至亲', '母子至亲'].some(k => d.relation.includes(k))) {
            return 0.75;
          }
          return 0;
        })
        .style('font-weight', 'normal')
        .style('font-size', '11px')
        .style('fill', 'var(--text-secondary)');
    }
  }

  renderNodes() {
    const nodes = this.nodeGroup.selectAll('g.graph-node')
      .data(this.activeNodes, d => d.id);

    nodes.exit().remove();

    const nodeEnter = nodes.enter()
      .append('g')
      .attr('class', 'graph-node')
      .call(d3.drag()
        .on('start', (e, d) => this.dragStarted(e, d))
        .on('drag', (e, d) => this.dragged(e, d))
        .on('end', (e, d) => this.dragEnded(e, d)))
      .on('click', (event, d) => {
        event.stopPropagation();
        this.selectNode(d);
      })
      .on('dblclick', (event, d) => {
        event.stopPropagation();
        this.togglePinNode(d);
      })
      .on('mouseenter', (event, d) => {
        this.hoveredNode = d;
        if (!this.selectedNode || this.selectedNode.id !== d.id) {
          this.highlightNeighbors(d);
          this.setNodeEnlarged(d, true, false); // 悬停微放大
        }
      })
      .on('mouseleave', (event, d) => {
        this.hoveredNode = null;
        if (!this.selectedNode) {
          this.resetHighlights();
          this.setNodeEnlarged(d, false);
        } else {
          this.highlightNeighbors(this.selectedNode);
          if (this.selectedNode.id !== d.id) {
            this.setNodeEnlarged(d, false);
          }
        }
      });

    // 悬浮/选中发光光晕
    nodeEnter.append('circle')
      .attr('class', 'node-halo')
      .attr('r', d => this.getNodeRadius(d) + 9);

    // 头像圆形（只加载图片，无任何文字遮挡）
    nodeEnter.append('circle')
      .attr('class', 'node-avatar-circle')
      .attr('r', d => this.getNodeRadius(d))
      .attr('fill', d => `url(#avatar-${d.id})`);

    // 典雅外边框金圈
    nodeEnter.append('circle')
      .attr('class', 'node-border')
      .attr('r', d => this.getNodeRadius(d))
      .attr('stroke', d => this.getClanColor(d.clan));

    // 姓名文字（位于头像下方，清晰利落）
    nodeEnter.append('text')
      .attr('class', 'node-label')
      .attr('y', d => this.getNodeRadius(d) + 16)
      .text(d => d.name);

    // 演员/身份副标签
    nodeEnter.append('text')
      .attr('class', 'node-sublabel')
      .attr('y', d => this.getNodeRadius(d) + 29)
      .text(d => d.actor ? `${d.actor} 饰` : (d.identity ? d.identity.slice(0, 5) : ''));

    // 固定图钉小图标
    nodeEnter.append('circle')
      .attr('class', 'node-pinned-indicator')
      .attr('r', 4.5)
      .attr('cx', d => this.getNodeRadius(d) * 0.707)
      .attr('cy', d => -this.getNodeRadius(d) * 0.707)
      .style('display', d => (d.fx !== null && d.fx !== undefined) ? 'block' : 'none');

    this.nodeElements = nodeEnter.merge(nodes);
  }

  // 物理模拟步进更新：动态拉伸连接线与平滑曲线计算
  tick() {
    if (this.linkElements) {
      this.linkElements.attr('d', d => {
        const sx = d.source.x;
        const sy = d.source.y;
        const tx = d.target.x;
        const ty = d.target.y;

        const dx = tx - sx;
        const dy = ty - sy;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;

        // 计算当前节点实时半径（若处于选中放大状态，动态贴合放大后的边缘）
        const isSourceEnlarged = (this.selectedNode && this.selectedNode.id === d.source.id);
        const isTargetEnlarged = (this.selectedNode && this.selectedNode.id === d.target.id);
        const sr = isSourceEnlarged ? this.getEnlargedRadius(d.source) : this.getNodeRadius(d.source);
        const tr = (isTargetEnlarged ? this.getEnlargedRadius(d.target) : this.getNodeRadius(d.target)) + 7;

        const startX = sx + (dx * sr) / dist;
        const startY = sy + (dy * sr) / dist;
        const endX = tx - (dx * tr) / dist;
        const endY = ty - (dy * tr) / dist;

        if (d.curvature && Math.abs(d.curvature) > 0.01) {
          const midX = (startX + endX) / 2;
          const midY = (startY + endY) / 2;
          const normX = -dy / dist;
          const normY = dx / dist;
          const ctrlX = midX + normX * dist * d.curvature;
          const ctrlY = midY + normY * dist * d.curvature;
          return `M${startX},${startY} Q${ctrlX},${ctrlY} ${endX},${endY}`;
        }

        return `M${startX},${startY} L${endX},${endY}`;
      });
    }

    if (this.linkLabelElements) {
      this.linkLabelElements
        .attr('x', d => {
          if (d.curvature && Math.abs(d.curvature) > 0.01) {
            const midX = (d.source.x + d.target.x) / 2;
            const normX = -(d.target.y - d.source.y);
            const dist = Math.sqrt(Math.pow(d.target.x - d.source.x, 2) + Math.pow(d.target.y - d.source.y, 2)) || 1;
            return midX + (normX / dist) * dist * d.curvature * 0.5;
          }
          return (d.source.x + d.target.x) / 2;
        })
        .attr('y', d => {
          if (d.curvature && Math.abs(d.curvature) > 0.01) {
            const midY = (d.source.y + d.target.y) / 2;
            const normY = (d.target.x - d.source.x);
            const dist = Math.sqrt(Math.pow(d.target.x - d.source.x, 2) + Math.pow(d.target.y - d.source.y, 2)) || 1;
            return midY + (normY / dist) * dist * d.curvature * 0.5;
          }
          return (d.source.y + d.target.y) / 2;
        });
    }

    if (this.nodeElements) {
      this.nodeElements.attr('transform', d => `translate(${d.x},${d.y})`);
    }

    this.updateMinimap();
  }

  // 拖拽逻辑：物理拉伸交互核心
  dragStarted(event, d) {
    if (!event.active && this.isSimulationRunning) {
      this.simulation.alphaTarget(0.2).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
    this.svg.style('cursor', 'grabbing');
  }

  dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  /**
   * 需求4：拉动后不要自动复位！
   * 拖拽释放后，保持当前拖拽落点坐标 (d.fx = d.x; d.fy = d.y)，绝不回弹！
   */
  dragEnded(event, d) {
    if (!event.active && this.isSimulationRunning) {
      this.simulation.alphaTarget(0);
    }
    this.svg.style('cursor', 'grab');

    // 永久保持拖拽目标位置，绝不复位
    d.fx = d.x;
    d.fy = d.y;
    this.pinnedNodes.add(d.id);
    this.updateNodePinIndicator(d);
  }

  // 双击切换节点固定/解除
  togglePinNode(d) {
    if (d.fx !== null && d.fx !== undefined) {
      d.fx = null;
      d.fy = null;
      this.pinnedNodes.delete(d.id);
    } else {
      d.fx = d.x;
      d.fy = d.y;
      this.pinnedNodes.add(d.id);
    }
    this.updateNodePinIndicator(d);
  }

  updateNodePinIndicator(d) {
    this.nodeElements.filter(n => n.id === d.id)
      .select('.node-pinned-indicator')
      .style('display', (d.fx !== null && d.fx !== undefined) ? 'block' : 'none');
  }

  unlockAllNodes() {
    this.activeNodes.forEach(n => {
      n.fx = null;
      n.fy = null;
    });
    this.pinnedNodes.clear();
    this.nodeElements.selectAll('.node-pinned-indicator').style('display', 'none');
    this.simulation.alpha(0.35).restart();
  }

  toggleSimulation() {
    if (this.isSimulationRunning) {
      this.simulation.stop();
      this.isSimulationRunning = false;
    } else {
      this.simulation.alpha(0.35).restart();
      this.isSimulationRunning = true;
    }
    return this.isSimulationRunning;
  }

  /**
   * 需求3：鼠标选中头像变大！
   * 选中的节点平滑放大至 1.68 倍，边框加粗高亮，并置于最顶层
   */
  selectNode(d) {
    // 如果之前有选中的节点，将其复原
    if (this.selectedNode && this.selectedNode.id !== d.id) {
      this.setNodeEnlarged(this.selectedNode, false);
    }

    this.selectedNode = d;
    this.nodeElements.classed('selected', n => n.id === d.id);
    
    // 平滑放大选中的节点
    this.setNodeEnlarged(d, true, true);

    this.highlightNeighbors(d);
    this.updateLabelVisibility();

    if (this.options.onNodeClick) {
      this.options.onNodeClick(d);
    }
  }

  clearSelection() {
    if (this.selectedNode) {
      this.setNodeEnlarged(this.selectedNode, false);
      this.selectedNode = null;
    }
    this.nodeElements.classed('selected', false);
    this.resetHighlights();
    this.updateLabelVisibility();

    if (this.options.onNodeClick) {
      this.options.onNodeClick(null);
    }
  }

  // 控制节点及其头像的平滑放大/复原动画
  setNodeEnlarged(d, isEnlarged, isFullSelect = false) {
    const targetElement = this.nodeElements.filter(n => n.id === d.id);
    if (targetElement.empty()) return;

    if (isEnlarged) {
      targetElement.raise(); // 置于最顶层，避免被其他连线遮挡
    }

    const r = isEnlarged ? (isFullSelect ? this.getEnlargedRadius(d) : Math.round(this.getNodeRadius(d) * 1.25)) : this.getNodeRadius(d);
    const duration = 280;

    targetElement.select('.node-avatar-circle')
      .transition()
      .duration(duration)
      .ease(d3.easeCubicOut)
      .attr('r', r);

    targetElement.select('.node-border')
      .transition()
      .duration(duration)
      .ease(d3.easeCubicOut)
      .attr('r', r)
      .style('stroke-width', isEnlarged ? (isFullSelect ? '4.5px' : '3.5px') : '2.5px');

    targetElement.select('.node-halo')
      .transition()
      .duration(duration)
      .ease(d3.easeCubicOut)
      .attr('r', r + (isFullSelect ? 12 : 8))
      .style('opacity', isEnlarged ? 1 : 0);

    targetElement.select('.node-label')
      .transition()
      .duration(duration)
      .ease(d3.easeCubicOut)
      .attr('y', r + 18)
      .style('font-size', isEnlarged && isFullSelect ? '14px' : '12px');

    targetElement.select('.node-sublabel')
      .transition()
      .duration(duration)
      .ease(d3.easeCubicOut)
      .attr('y', r + 33)
      .style('font-size', isEnlarged && isFullSelect ? '11px' : '10px');

    targetElement.select('.node-pinned-indicator')
      .transition()
      .duration(duration)
      .ease(d3.easeCubicOut)
      .attr('cx', r * 0.707)
      .attr('cy', -r * 0.707);
  }

  // 平滑聚焦并飞向指定节点 (Fly-to)
  flyToNode(nodeId) {
    const node = this.activeNodes.find(n => n.id === nodeId);
    if (!node) return;

    this.selectNode(node);

    const { width, height } = this.getDimensions();
    const transform = d3.zoomIdentity
      .translate(width / 2, height / 2)
      .scale(1.2)
      .translate(-node.x, -node.y);

    this.svg.transition()
      .duration(850)
      .ease(d3.easeCubicOut)
      .call(this.zoom.transform, transform);
  }

  // 高亮一度关联邻居与连线（聚光灯模式：彻底隐藏无关背景文字与连线）
  highlightNeighbors(centerNode) {
    const neighborIds = new Set();
    neighborIds.add(centerNode.id);
    const activeLinkKeys = new Set();

    this.activeLinks.forEach(l => {
      const s = l.source.id || l.source;
      const t = l.target.id || l.target;
      if (s === centerNode.id) {
        neighborIds.add(t);
        activeLinkKeys.add(`${s}_${t}_${l.relation}`);
      } else if (t === centerNode.id) {
        neighborIds.add(s);
        activeLinkKeys.add(`${s}_${t}_${l.relation}`);
      }
    });

    // 重点：彻底隐藏所有无关背景节点的文字与介绍，杜绝干扰阅读！
    this.nodeElements.each(function(n) {
      const isNeighbor = neighborIds.has(n.id);
      const isCenter = n.id === centerNode.id;
      const el = d3.select(this);

      if (isNeighbor) {
        el.style('opacity', 1)
          .style('pointer-events', 'auto');
        el.select('.node-label')
          .style('display', 'block')
          .style('opacity', 1);
        el.select('.node-sublabel')
          .style('display', 'block')
          .style('opacity', 1);
        el.select('.node-border')
          .style('stroke-width', isCenter ? '5px' : '3.5px')
          .style('filter', isCenter ? 'url(#glow)' : null);
      } else {
        // 无关背景节点：文字全部隐藏！透明度压至极淡轮廓 (0.03)，背景绝无文字干扰
        el.style('opacity', 0.03)
          .style('pointer-events', 'none');
        el.select('.node-label')
          .style('display', 'none')
          .style('opacity', 0);
        el.select('.node-sublabel')
          .style('display', 'none')
          .style('opacity', 0);
        el.select('.node-border')
          .style('stroke-width', '1px')
          .style('filter', null);
      }
    });

    // 连线：仅展示当前人物相关的连线，无关连线彻底隐藏
    this.linkElements
      .style('display', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return activeLinkKeys.has(`${s}_${t}_${l.relation}`) ? 'block' : 'none';
      })
      .style('opacity', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return activeLinkKeys.has(`${s}_${t}_${l.relation}`) ? 1 : 0;
      })
      .classed('highlighted', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return activeLinkKeys.has(`${s}_${t}_${l.relation}`);
      });

    this.updateLabelVisibility();
  }

  resetHighlights() {
    this.nodeElements.each(function(n) {
      const el = d3.select(this);
      el.style('opacity', 1)
        .style('pointer-events', 'auto');
      el.select('.node-label')
        .style('display', 'block')
        .style('opacity', 1);
      el.select('.node-sublabel')
        .style('display', 'block')
        .style('opacity', 1);
      el.select('.node-border')
        .style('stroke-width', '2.5px')
        .style('filter', null);
    });

    this.linkElements
      .style('display', 'block')
      .style('opacity', 0.28)
      .classed('highlighted', false);

    this.updateLabelVisibility();
  }

  highlightPath(pathNodeIds, pathEdgeKeys) {
    const nodeSet = new Set(pathNodeIds);
    const edgeSet = new Set(pathEdgeKeys);

    this.nodeElements.each(function(n) {
      const inPath = nodeSet.has(n.id);
      const el = d3.select(this);
      if (inPath) {
        el.style('opacity', 1).style('pointer-events', 'auto');
        el.select('.node-label').style('display', 'block').style('opacity', 1);
        el.select('.node-sublabel').style('display', 'block').style('opacity', 1);
        el.select('.node-border').style('stroke-width', '4.5px').style('filter', 'url(#glow)');
      } else {
        el.style('opacity', 0.03).style('pointer-events', 'none');
        el.select('.node-label').style('display', 'none').style('opacity', 0);
        el.select('.node-sublabel').style('display', 'none').style('opacity', 0);
        el.select('.node-border').style('stroke-width', '1px').style('filter', null);
      }
    });

    this.linkElements
      .style('display', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return (edgeSet.has(`${s}->${t}`) || edgeSet.has(`${t}->${s}`)) ? 'block' : 'none';
      })
      .style('opacity', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return (edgeSet.has(`${s}->${t}`) || edgeSet.has(`${t}->${s}`)) ? 1 : 0;
      })
      .classed('highlighted', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return edgeSet.has(`${s}->${t}`) || edgeSet.has(`${t}->${s}`);
      });

    this.linkLabelElements
      .style('display', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return (edgeSet.has(`${s}->${t}`) || edgeSet.has(`${t}->${s}`)) ? 'block' : 'none';
      })
      .style('opacity', l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        return (edgeSet.has(`${s}->${t}`) || edgeSet.has(`${t}->${s}`)) ? 1 : 0;
      });
  }

  fitToView(duration = 850) {
    if (this.activeNodes.length === 0) return;

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    this.activeNodes.forEach(n => {
      if (n.x < minX) minX = n.x;
      if (n.x > maxX) maxX = n.x;
      if (n.y < minY) minY = n.y;
      if (n.y > maxY) maxY = n.y;
    });

    const padding = 120;
    const { width, height } = this.getDimensions();
    const graphWidth = maxX - minX + padding * 2;
    const graphHeight = maxY - minY + padding * 2;

    const scale = Math.min(2.0, Math.max(0.2, 0.9 / Math.max(graphWidth / width, graphHeight / height)));
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    const transform = d3.zoomIdentity
      .translate(width / 2, height / 2)
      .scale(scale)
      .translate(-centerX, -centerY);

    this.svg.transition()
      .duration(duration)
      .ease(d3.easeCubicOut)
      .call(this.zoom.transform, transform);
  }

  zoomIn() {
    this.svg.transition().duration(300).call(this.zoom.scaleBy, 1.3);
  }

  zoomOut() {
    this.svg.transition().duration(300).call(this.zoom.scaleBy, 0.77);
  }

  bindMinimap(canvasSelector) {
    this.minimapCanvas = document.querySelector(canvasSelector);
    if (!this.minimapCanvas) return;
    this.minimapCtx = this.minimapCanvas.getContext('2d');
  }

  updateMinimap() {
    if (!this.minimapCtx || !this.minimapCanvas) return;

    const cvs = this.minimapCanvas;
    const ctx = this.minimapCtx;
    const w = cvs.width = cvs.offsetWidth * 2;
    const h = cvs.height = cvs.offsetHeight * 2;

    ctx.clearRect(0, 0, w, h);
    if (this.activeNodes.length === 0) return;

    let minX = -1200, maxX = 1200, minY = -1000, maxY = 1000;
    this.activeNodes.forEach(n => {
      if (n.x < minX) minX = n.x;
      if (n.x > maxX) maxX = n.x;
      if (n.y < minY) minY = n.y;
      if (n.y > maxY) maxY = n.y;
    });

    const pad = 180;
    const gw = (maxX - minX) + pad * 2;
    const gh = (maxY - minY) + pad * 2;
    const scale = Math.min(w / gw, h / gh);

    const toMapX = (x) => (x - (minX - pad)) * scale;
    const toMapY = (y) => (y - (minY - pad)) * scale;

    ctx.strokeStyle = 'rgba(212, 175, 55, 0.12)';
    ctx.lineWidth = 1;
    this.activeLinks.forEach(l => {
      ctx.beginPath();
      ctx.moveTo(toMapX(l.source.x), toMapY(l.source.y));
      ctx.lineTo(toMapX(l.target.x), toMapY(l.target.y));
      ctx.stroke();
    });

    this.activeNodes.forEach(n => {
      ctx.fillStyle = this.getClanColor(n.clan);
      ctx.beginPath();
      ctx.arc(toMapX(n.x), toMapY(n.y), (n.tier <= 2 ? 4 : 2.5), 0, Math.PI * 2);
      ctx.fill();
    });
  }

  updateForces({ linkDistance, linkStrength, chargeStrength }) {
    if (linkDistance !== undefined) {
      this.options.linkDistance = linkDistance;
      this.simulation.force('link').distance(d => this.getLinkDistance(d));
    }
    if (linkStrength !== undefined) {
      this.options.linkStrength = linkStrength;
      this.simulation.force('link').strength(linkStrength);
    }
    if (chargeStrength !== undefined) {
      this.options.chargeStrength = chargeStrength;
      this.simulation.force('charge').strength(d => this.getChargeStrength(d));
    }
    this.simulation.alpha(0.35).restart();
  }
}

window.HonglouGraph = HonglouGraph;
