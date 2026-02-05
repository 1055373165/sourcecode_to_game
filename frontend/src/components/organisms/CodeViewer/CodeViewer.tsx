import React, { useRef, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import { cn } from '@utils/index'
import { Language } from '@apptypes/index'
import type { editor } from 'monaco-editor'

export interface CodeViewerProps {
    code: string
    language: Language
    highlightedLines?: number[]
    readOnly?: boolean
    theme?: 'vs-dark' | 'light'
    showLineNumbers?: boolean
    showMinimap?: boolean
    height?: string | number
    className?: string
    onLineClick?: (lineNumber: number) => void
}

export const CodeViewer: React.FC<CodeViewerProps> = ({
    code,
    language,
    highlightedLines = [],
    readOnly = true,
    theme = 'vs-dark',
    showLineNumbers = true,
    showMinimap = true,
    height = '500px',
    className,
    onLineClick,
}) => {
    const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
    const decorationsRef = useRef<string[]>([])

    const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor) => {
        editorRef.current = editor

        // Add line click handler
        if (onLineClick) {
            editor.onMouseDown((e) => {
                if (e.target.position) {
                    onLineClick(e.target.position.lineNumber)
                }
            })
        }

        // Initial highlight
        updateHighlights()
    }

    const updateHighlights = () => {
        if (!editorRef.current) return

        // Remove previous decorations
        if (decorationsRef.current.length > 0) {
            editorRef.current.deltaDecorations(decorationsRef.current, [])
        }

        // Add new decorations for highlighted lines
        const newDecorations = highlightedLines.map((lineNumber) => ({
            range: {
                startLineNumber: lineNumber,
                startColumn: 1,
                endLineNumber: lineNumber,
                endColumn: 1,
            },
            options: {
                isWholeLine: true,
                className: 'highlighted-line',
                glyphMarginClassName: 'highlighted-line-glyph',
                overviewRuler: {
                    color: 'rgba(59, 130, 246, 0.6)',
                    position: 2, // editor.OverviewRulerLane.Center
                },
            },
        }))

        decorationsRef.current = editorRef.current.deltaDecorations([], newDecorations)
    }

    useEffect(() => {
        updateHighlights()
    }, [highlightedLines])

    const getLanguageId = (lang: Language): string => {
        switch (lang) {
            case Language.PYTHON:
                return 'python'
            case Language.GOLANG:
                return 'go'
            default:
                return 'plaintext'
        }
    }

    return (
        <div className={cn('rounded-lg overflow-hidden border border-gray-300 dark:border-gray-700', className)}>
            <style>
                {`
          .highlighted-line {
            background-color: rgba(59, 130, 246, 0.15);
            border-left: 3px solid rgba(59, 130, 246, 0.8);
          }
          
          .highlighted-line-glyph {
            background-color: rgba(59, 130, 246, 0.6);
            width: 5px !important;
            margin-left: 3px;
          }
          
          .monaco-editor .margin {
            background-color: transparent !important;
          }
        `}
            </style>

            <Editor
                height={height}
                language={getLanguageId(language)}
                value={code}
                theme={theme}
                onMount={handleEditorDidMount}
                options={{
                    readOnly,
                    lineNumbers: showLineNumbers ? 'on' : 'off',
                    minimap: {
                        enabled: showMinimap,
                    },
                    scrollBeyondLastLine: false,
                    fontSize: 14,
                    fontFamily: 'Fira Code, Consolas, monospace',
                    lineHeight: 20,
                    padding: { top: 10, bottom: 10 },
                    automaticLayout: true,
                    scrollbar: {
                        vertical: 'auto',
                        horizontal: 'auto',
                        useShadows: false,
                        verticalScrollbarSize: 10,
                        horizontalScrollbarSize: 10,
                    },
                    renderLineHighlight: 'line',
                    cursorBlinking: readOnly ? 'solid' : 'blink',
                    contextmenu: !readOnly,
                    quickSuggestions: !readOnly,
                    folding: true,
                    foldingStrategy: 'indentation',
                    showFoldingControls: 'mouseover',
                }}
                loading={
                    <div className="flex items-center justify-center h-full bg-gray-50 dark:bg-gray-900">
                        <div className="text-gray-500 dark:text-gray-400">Loading editor...</div>
                    </div>
                }
            />
        </div>
    )
}
