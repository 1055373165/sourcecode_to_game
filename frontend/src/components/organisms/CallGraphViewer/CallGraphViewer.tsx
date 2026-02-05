import React, { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { cn } from '@utils/index'
import { type CodeNode, type CallEdge, NodeType } from '@apptypes/index'

export interface CallGraphViewerProps {
    nodes: CodeNode[]
    edges: CallEdge[]
    entryPoints: string[]
    onNodeClick?: (node: CodeNode) => void
    width?: number
    height?: number
    className?: string
}

interface D3Node extends d3.SimulationNodeDatum {
    id: string
    data: CodeNode
    isEntry: boolean
}

interface D3Link extends d3.SimulationLinkDatum<D3Node> {
    source: string | D3Node
    target: string | D3Node
    data: CallEdge
}

export const CallGraphViewer: React.FC<CallGraphViewerProps> = ({
    nodes,
    edges,
    entryPoints,
    onNodeClick,
    width = 800,
    height = 600,
    className,
}) => {
    const svgRef = useRef<SVGSVGElement>(null)
    const [selectedNode, setSelectedNode] = useState<string | null>(null)

    useEffect(() => {
        if (!svgRef.current || nodes.length === 0) return

        // Clear previous content
        d3.select(svgRef.current).selectAll('*').remove()

        const svg = d3.select(svgRef.current)
            .attr('viewBox', [0, 0, width, height])
            .attr('style', 'max-width: 100%; height: auto;')

        // Create container group for zoom
        const g = svg.append('g')

        // Add zoom behavior
        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                g.attr('transform', event.transform)
            })

        svg.call(zoom)

        // Prepare data
        const d3Nodes: D3Node[] = nodes.map(node => ({
            id: node.id,
            data: node,
            isEntry: entryPoints.includes(node.id),
        }))

        const d3Links: D3Link[] = edges.map(edge => ({
            source: edge.from_node,
            target: edge.to_node,
            data: edge,
        }))

        // Create force simulation
        const simulation = d3.forceSimulation(d3Nodes)
            .force('link', d3.forceLink<D3Node, D3Link>(d3Links)
                .id(d => d.id)
                .distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(40))

        // Create arrow markers
        svg.append('defs').selectAll('marker')
            .data(['arrow'])
            .join('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#94a3b8')

        // Draw links
        const link = g.append('g')
            .selectAll('line')
            .data(d3Links)
            .join('line')
            .attr('stroke', '#94a3b8')
            .attr('stroke-width', d => Math.min(d.data.call_count / 2 + 1, 4))
            .attr('stroke-opacity', 0.6)
            .attr('marker-end', 'url(#arrow)')

        // Draw nodes
        const node = g.append('g')
            .selectAll('g')
            .data(d3Nodes)
            .join('g')
            .attr('cursor', 'pointer')
            .call(d3.drag<SVGGElement, D3Node>()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended) as any)

        // Node circles
        node.append('circle')
            .attr('r', d => d.isEntry ? 25 : 20)
            .attr('fill', d => getNodeColor(d))
            .attr('stroke', d => d.isEntry ? '#f59e0b' : '#cbd5e1')
            .attr('stroke-width', d => d.isEntry ? 3 : 2)
            .on('click', (event, d) => {
                event.stopPropagation()
                setSelectedNode(d.id)
                if (onNodeClick) {
                    onNodeClick(d.data)
                }
            })

        // Node labels
        node.append('text')
            .text(d => d.data.name)
            .attr('text-anchor', 'middle')
            .attr('dy', d => d.isEntry ? 40 : 35)
            .attr('font-size', 12)
            .attr('font-weight', d => d.isEntry ? 'bold' : 'normal')
            .attr('fill', 'currentColor')
            .style('pointer-events', 'none')

        // Node type icon
        node.append('text')
            .text(d => getNodeIcon(d.data.node_type))
            .attr('text-anchor', 'middle')
            .attr('dy', 5)
            .attr('font-size', 16)
            .style('pointer-events', 'none')

        // Update positions on simulation tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => (d.source as D3Node).x!)
                .attr('y1', d => (d.source as D3Node).y!)
                .attr('x2', d => (d.target as D3Node).x!)
                .attr('y2', d => (d.target as D3Node).y!)

            node.attr('transform', d => `translate(${d.x},${d.y})`)
        })

        // Drag functions
        function dragstarted(event: any, d: D3Node) {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
        }

        function dragged(event: any, d: D3Node) {
            d.fx = event.x
            d.fy = event.y
        }

        function dragended(event: any, d: D3Node) {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
        }

        // Cleanup
        return () => {
            simulation.stop()
        }
    }, [nodes, edges, entryPoints, width, height, onNodeClick])

    const getNodeColor = (node: D3Node) => {
        if (selectedNode === node.id) return '#3b82f6'
        if (node.isEntry) return '#fbbf24'

        switch (node.data.node_type) {
            case NodeType.FUNCTION:
                return '#10b981'
            case NodeType.METHOD:
                return '#8b5cf6'
            case NodeType.CLASS:
                return '#ec4899'
            default:
                return '#6b7280'
        }
    }

    const getNodeIcon = (nodeType: NodeType) => {
        switch (nodeType) {
            case NodeType.FUNCTION:
                return '⚡'
            case NodeType.METHOD:
                return '🔧'
            case NodeType.CLASS:
                return '📦'
            default:
                return '◯'
        }
    }

    return (
        <div className={cn('bg-white dark:bg-dark-surface rounded-lg border border-gray-300 dark:border-gray-700 overflow-hidden', className)}>
            {/* Legend */}
            <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <div className="flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-yellow-400 border-2 border-yellow-600"></div>
                        <span className="text-gray-700 dark:text-gray-300">Entry Point</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-lg">⚡</span>
                        <span className="text-gray-700 dark:text-gray-300">Function</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🔧</span>
                        <span className="text-gray-700 dark:text-gray-300">Method</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-lg">📦</span>
                        <span className="text-gray-700 dark:text-gray-300">Class</span>
                    </div>
                </div>
            </div>

            {/* Graph */}
            <div className="relative" style={{ height }}>
                <svg ref={svgRef} className="w-full h-full"></svg>

                {nodes.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <p className="text-gray-500 dark:text-gray-400">No call graph data</p>
                    </div>
                )}
            </div>

            {/* Controls hint */}
            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-xs text-gray-600 dark:text-gray-400">
                <p>💡 Drag nodes to rearrange • Scroll to zoom • Click nodes for details</p>
            </div>
        </div>
    )
}
