/**
 * 87版《红楼梦》人物关系寻径器 (BFS / Shortest Relationship Path Finder)
 */

class RelationshipPathFinder {
  constructor(nodes, links) {
    this.nodes = nodes || [];
    this.links = links || [];
    this.buildAdjacency();
  }

  update(nodes, links) {
    this.nodes = nodes || [];
    this.links = links || [];
    this.buildAdjacency();
  }

  buildAdjacency() {
    this.adj = new Map();
    this.nodes.forEach(n => this.adj.set(n.id, []));

    this.links.forEach(link => {
      const s = typeof link.source === 'object' ? link.source.id : link.source;
      const t = typeof link.target === 'object' ? link.target.id : link.target;

      if (!this.adj.has(s)) this.adj.set(s, []);
      if (!this.adj.has(t)) this.adj.set(t, []);

      this.adj.get(s).push({ target: t, relation: link.relation, type: link.type, desc: link.desc, direction: 'forward' });
      this.adj.get(t).push({ target: s, relation: link.relation, type: link.type, desc: link.desc, direction: 'backward' });
    });
  }

  // 广度优先搜索寻找最短关系链
  findShortestPath(startId, targetId) {
    if (startId === targetId) return null;
    if (!this.adj.has(startId) || !this.adj.has(targetId)) return null;

    const queue = [[startId]];
    const visited = new Set([startId]);
    const edgeMap = new Map(); // target -> edge info

    while (queue.length > 0) {
      const path = queue.shift();
      const current = path[path.length - 1];

      if (current === targetId) {
        // 构建完整路径解析结果
        const steps = [];
        for (let i = 0; i < path.length - 1; i++) {
          const from = path[i];
          const to = path[i + 1];
          const edges = this.adj.get(from).filter(e => e.target === to);
          steps.push({
            from,
            to,
            relation: edges[0]?.relation || '关联网',
            type: edges[0]?.type || 'default',
            desc: edges[0]?.desc || ''
          });
        }
        return {
          nodes: path,
          steps: steps,
          length: path.length - 1
        };
      }

      const neighbors = this.adj.get(current) || [];
      for (const edge of neighbors) {
        if (!visited.has(edge.target)) {
          visited.add(edge.target);
          queue.push([...path, edge.target]);
        }
      }
    }

    return null; // 无连通路径
  }
}

window.RelationshipPathFinder = RelationshipPathFinder;
