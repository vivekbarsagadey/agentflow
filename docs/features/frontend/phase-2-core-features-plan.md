---
goal: AgentFlow Studio Phase 2 - Core Features Implementation Plan
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Team
status: 'Planned'
tags: ['feature', 'frontend', 'phase-2', 'execution', 'queues']
---

# AgentFlow Studio - Phase 2: Core Features Implementation Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

**Duration:** 8 Weeks (Weeks 9-16)  
**Goal:** Complete production-ready feature set with execution, queue management, UI polish, and dashboard enhancements.

---

## 1. Requirements & Constraints

### Core Requirements

- **REQ-020**: Must execute workflows with test input data
- **REQ-021**: Must display execution results with metrics (time, tokens, cost)
- **REQ-022**: Must support queue configuration with bandwidth settings
- **REQ-023**: Must implement undo/redo for all canvas operations
- **REQ-024**: Must provide keyboard shortcuts for all major actions
- **REQ-025**: Must support dark mode with consistent theming
- **REQ-026**: Must show toast notifications for all user actions
- **REQ-027**: Must handle errors gracefully with user-friendly messages
- **REQ-028**: Must implement dashboard search and filtering
- **REQ-029**: Must support workflow templates gallery
- **REQ-030**: Must allow workflow duplication

### Performance Requirements

- **PERF-001**: Execution status must update within 100ms
- **PERF-002**: Undo/redo must complete within 50ms
- **PERF-003**: Search results must appear within 200ms
- **PERF-004**: Toast notifications must not block UI

### UX Requirements

- **UX-001**: Execution progress must be visually clear
- **UX-002**: Error messages must include actionable next steps
- **UX-003**: Loading states must be consistent across all components
- **UX-004**: Keyboard shortcuts must be discoverable (help dialog)

---

## 2. Implementation Steps

### Phase 2.1: Execution Panel Component (Week 9-10)

**GOAL-014:** Implement workflow execution with input form, progress tracking, and results display.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-187 | Create `components/ExecutionPanel.tsx` bottom panel component | | |
| TASK-188 | Add "Execute" button to designer toolbar | | |
| TASK-189 | Create input form with JSON editor for test data | | |
| TASK-190 | Implement JSON editor with syntax highlighting | | |
| TASK-191 | Add input validation (valid JSON check) | | |
| TASK-192 | Create API client function `executeWorkflow()` | | |
| TASK-193 | Call backend `/workflows/execute` endpoint | | |
| TASK-194 | Handle streaming responses (if supported) | | |
| TASK-195 | Display execution status indicator (running, success, failed) | | |
| TASK-196 | Implement progress visualization on canvas (highlight active nodes) | | |
| TASK-197 | Add execution time tracker with live updates | | |
| TASK-198 | Create "Cancel Execution" button and handler | | |
| TASK-199 | Display final output in formatted JSON viewer | | |
| TASK-200 | Show execution metrics (tokens used, cost, node times) | | |
| TASK-201 | Add state transitions view (step-by-step execution log) | | |
| TASK-202 | Display error details if execution fails | | |
| TASK-203 | Add keyboard shortcut (Ctrl+Shift+E) for execute | | |
| TASK-204 | Implement execution history (last 10 runs) | | |
| TASK-205 | Add "Export Results" button (save as JSON) | | |
| TASK-206 | Style panel with tabs (Input, Output, Metrics, History) | | |

**Acceptance Criteria:**
- ✅ User can input test data and execute workflow
- ✅ Execution progress displays in real-time
- ✅ Results show clearly with metrics
- ✅ Errors are displayed with details
- ✅ Execution can be cancelled mid-run
- ✅ History tracks recent executions

---

### Phase 2.2: Queue Editor Component (Week 11-12)

**GOAL-015:** Implement queue configuration UI with bandwidth settings and visualization.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-207 | Create `components/QueueEditor.tsx` component | | |
| TASK-208 | Add queue state to Zustand store | | |
| TASK-209 | Create queue list view (table or cards) | | |
| TASK-210 | Add "Create Queue" button and modal | | |
| TASK-211 | Implement queue form (id, from, to) | | |
| TASK-212 | Add bandwidth configuration section | | |
| TASK-213 | Create inputs for max_messages_per_second | | |
| TASK-214 | Create inputs for max_requests_per_minute | | |
| TASK-215 | Create inputs for max_tokens_per_minute | | |
| TASK-216 | Implement sub-queue configuration (id, weight) | | |
| TASK-217 | Add queue validation (ensure from/to nodes exist) | | |
| TASK-218 | Create queue visualization on canvas (dashed line overlay) | | |
| TASK-219 | Add queue icon/badge on edges | | |
| TASK-220 | Implement queue edit functionality | | |
| TASK-221 | Implement queue deletion with confirmation | | |
| TASK-222 | Add queue presets (Low, Medium, High bandwidth) | | |
| TASK-223 | Show queue usage in properties panel when edge selected | | |
| TASK-224 | Test queue creation and association with edges | | |

**Acceptance Criteria:**
- ✅ Queues can be created between nodes
- ✅ Bandwidth settings can be configured
- ✅ Sub-queues can be added with weights
- ✅ Queues validate correctly
- ✅ Queue visualization appears on canvas
- ✅ Queue presets simplify configuration

---

### Phase 2.3: Undo/Redo Implementation (Week 13)

**GOAL-016:** Implement undo/redo functionality for all canvas and workflow operations.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-225 | Add history state to Zustand store (past, present, future) | | |
| TASK-226 | Implement history middleware for store | | |
| TASK-227 | Create `undo()` action | | |
| TASK-228 | Create `redo()` action | | |
| TASK-229 | Add undo/redo buttons to toolbar | | |
| TASK-230 | Implement keyboard shortcuts (Ctrl+Z, Ctrl+Y) | | |
| TASK-231 | Track node add/remove/update operations | | |
| TASK-232 | Track edge add/remove operations | | |
| TASK-233 | Track source add/remove/update operations | | |
| TASK-234 | Track queue add/remove/update operations | | |
| TASK-235 | Show undo/redo availability (disable when no history) | | |
| TASK-236 | Add undo/redo tooltips with operation descriptions | | |
| TASK-237 | Limit history depth (50 operations max) | | |
| TASK-238 | Clear undo history when loading new workflow | | |
| TASK-239 | Test undo/redo with complex operations | | |
| TASK-240 | Ensure undo/redo updates unsaved changes flag | | |

**Acceptance Criteria:**
- ✅ Undo reverts last operation correctly
- ✅ Redo re-applies undone operation
- ✅ Keyboard shortcuts work consistently
- ✅ History depth is limited to prevent memory issues
- ✅ All operations support undo/redo
- ✅ Buttons disabled when no history available

---

### Phase 2.4: Keyboard Shortcuts System (Week 13)

**GOAL-017:** Implement comprehensive keyboard shortcuts for all major actions.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-241 | Create keyboard shortcut configuration object | | |
| TASK-242 | Implement global keyboard event listener | | |
| TASK-243 | Add Ctrl+N (New Workflow) | | |
| TASK-244 | Add Ctrl+O (Open Workflow dialog) | | |
| TASK-245 | Add Ctrl+S (Save Workflow) | | |
| TASK-246 | Add Ctrl+Shift+S (Save As) | | |
| TASK-247 | Add Ctrl+Z (Undo) | | |
| TASK-248 | Add Ctrl+Y (Redo) | | |
| TASK-249 | Add Ctrl+C (Copy selected nodes) | | |
| TASK-250 | Add Ctrl+V (Paste nodes) | | |
| TASK-251 | Add Ctrl+D (Duplicate selected) | | |
| TASK-252 | Add Delete (Delete selected) | | |
| TASK-253 | Add Ctrl+A (Select all nodes) | | |
| TASK-254 | Add Ctrl+Shift+V (Validate) | | |
| TASK-255 | Add Ctrl+Shift+E (Execute) | | |
| TASK-256 | Add Ctrl+K (Command palette) | | |
| TASK-257 | Add F11 (Fullscreen canvas) | | |
| TASK-258 | Add Escape (Deselect all) | | |
| TASK-259 | Create keyboard shortcuts help dialog (?) | | |
| TASK-260 | Show keyboard shortcuts in tooltips | | |
| TASK-261 | Prevent shortcuts when input fields focused | | |
| TASK-262 | Test shortcuts on different browsers and OSs | | |

**Acceptance Criteria:**
- ✅ All major actions have keyboard shortcuts
- ✅ Shortcuts work consistently across browsers
- ✅ Help dialog lists all shortcuts
- ✅ Shortcuts respect input field focus
- ✅ Mac users see Cmd instead of Ctrl
- ✅ No conflicts with browser shortcuts

---

### Phase 2.5: Dark Mode Implementation (Week 14)

**GOAL-018:** Implement comprehensive dark mode with consistent theming.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-263 | Configure `next-themes` provider in root layout | | |
| TASK-264 | Define dark mode color palette in Tailwind config | | |
| TASK-265 | Update all components with `dark:` variants | | |
| TASK-266 | Style WorkflowCanvas for dark mode | | |
| TASK-267 | Style NodePalette for dark mode | | |
| TASK-268 | Style PropertiesPanel for dark mode | | |
| TASK-269 | Style SourceEditor for dark mode | | |
| TASK-270 | Style JsonPreview with dark syntax highlighting | | |
| TASK-271 | Style ValidationPanel for dark mode | | |
| TASK-272 | Style ExecutionPanel for dark mode | | |
| TASK-273 | Style QueueEditor for dark mode | | |
| TASK-274 | Style Dashboard for dark mode | | |
| TASK-275 | Update custom node components for dark mode | | |
| TASK-276 | Style modals and dialogs for dark mode | | |
| TASK-277 | Create theme toggle button in header | | |
| TASK-278 | Add system theme detection | | |
| TASK-279 | Persist theme preference in localStorage | | |
| TASK-280 | Test all components in both themes | | |

**Acceptance Criteria:**
- ✅ Dark mode toggle switches theme instantly
- ✅ All components have proper dark mode styles
- ✅ Text contrast meets WCAG AA standards
- ✅ Theme preference persists across sessions
- ✅ System theme is respected by default
- ✅ No style flashes on page load

---

### Phase 2.6: Toast Notifications System (Week 14)

**GOAL-019:** Implement toast notifications for all user actions and feedback.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-281 | Install `sonner` or `react-hot-toast` library | | |
| TASK-282 | Configure toast provider in root layout | | |
| TASK-283 | Create toast utility functions (success, error, info, warning) | | |
| TASK-284 | Add success toast for workflow saved | | |
| TASK-285 | Add error toast for save failure | | |
| TASK-286 | Add success toast for validation passed | | |
| TASK-287 | Add error toast for validation failed | | |
| TASK-288 | Add success toast for execution completed | | |
| TASK-289 | Add error toast for execution failed | | |
| TASK-290 | Add success toast for node/source created | | |
| TASK-291 | Add info toast for unsaved changes warning | | |
| TASK-292 | Add toast for copy to clipboard actions | | |
| TASK-293 | Add toast for file export/import | | |
| TASK-294 | Configure toast auto-dismiss duration (3-5s) | | |
| TASK-295 | Add action buttons to toasts (undo, retry) | | |
| TASK-296 | Style toasts for light and dark mode | | |
| TASK-297 | Position toasts appropriately (top-right recommended) | | |
| TASK-298 | Test toast queue (multiple simultaneous toasts) | | |

**Acceptance Criteria:**
- ✅ Toasts appear for all major actions
- ✅ Success, error, info, warning types are distinct
- ✅ Toasts auto-dismiss after appropriate time
- ✅ Toasts are accessible (screen reader support)
- ✅ Toast position doesn't block important UI
- ✅ Multiple toasts stack cleanly

---

### Phase 2.7: Error Handling & User Feedback (Week 14)

**GOAL-020:** Implement comprehensive error handling with user-friendly messages.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-299 | Create error boundary components | | |
| TASK-300 | Add page-level error boundary | | |
| TASK-301 | Add component-level error boundaries (canvas, panels) | | |
| TASK-302 | Create fallback UI for errors | | |
| TASK-303 | Implement error logging (console in dev, service in prod) | | |
| TASK-304 | Create error message mapping (API error → user message) | | |
| TASK-305 | Add retry buttons for failed operations | | |
| TASK-306 | Implement network error detection | | |
| TASK-307 | Show offline indicator when backend unreachable | | |
| TASK-308 | Add loading states for all async operations | | |
| TASK-309 | Create skeleton loaders for data fetching | | |
| TASK-310 | Add spinners for quick operations | | |
| TASK-311 | Add progress bars for long operations | | |
| TASK-312 | Disable UI during critical operations | | |
| TASK-313 | Test error scenarios (network failure, validation errors) | | |
| TASK-314 | Ensure no console errors in production build | | |

**Acceptance Criteria:**
- ✅ Errors are caught and displayed gracefully
- ✅ User sees actionable error messages
- ✅ Retry buttons work for recoverable errors
- ✅ Loading states are consistent
- ✅ Offline state is clearly communicated
- ✅ No unhandled promise rejections

---

### Phase 2.8: Dashboard Enhancements (Week 15-16)

**GOAL-021:** Enhance dashboard with search, filter, and workflow management features.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-315 | Add search input to dashboard header | | |
| TASK-316 | Implement real-time search filtering | | |
| TASK-317 | Add filter dropdown (All, Draft, Validated, Deployed) | | |
| TASK-318 | Add sort dropdown (Name, Date, Last Modified) | | |
| TASK-319 | Implement grid/list view toggle | | |
| TASK-320 | Create workflow card component with thumbnail | | |
| TASK-321 | Generate workflow thumbnail (canvas snapshot) | | |
| TASK-322 | Add workflow metadata display (node count, status) | | |
| TASK-323 | Add quick actions menu (Open, Duplicate, Delete, Export) | | |
| TASK-324 | Implement "Duplicate Workflow" action | | |
| TASK-325 | Add confirmation dialog for delete | | |
| TASK-326 | Create "Recent Workflows" section (last 5 opened) | | |
| TASK-327 | Implement workflow pinning (favorites) | | |
| TASK-328 | Add "Pinned Workflows" section | | |
| TASK-329 | Style dashboard with responsive grid | | |
| TASK-330 | Add empty state for each section | | |
| TASK-331 | Implement pagination (20 workflows per page) | | |
| TASK-332 | Add loading skeleton for workflow cards | | |
| TASK-333 | Test dashboard with 100+ workflows | | |

**Acceptance Criteria:**
- ✅ Search filters workflows instantly
- ✅ Filters and sort work correctly
- ✅ Grid/list view toggle is smooth
- ✅ Thumbnails generate correctly
- ✅ Duplicate creates exact copy with new ID
- ✅ Recent and pinned sections function properly

---

### Phase 2.9: Workflow Templates (Week 15-16)

**GOAL-022:** Create workflow templates gallery for quick workflow creation.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-334 | Create templates data structure (JSON files) | | |
| TASK-335 | Design 5 starter templates (Simple LLM, Image Generation, etc.) | | |
| TASK-336 | Add "Templates" tab to dashboard | | |
| TASK-337 | Create template card component | | |
| TASK-338 | Add template preview modal | | |
| TASK-339 | Implement "Use Template" button | | |
| TASK-340 | Load template into designer with new workflow ID | | |
| TASK-341 | Add template categories (Common Patterns, Use Cases) | | |
| TASK-342 | Implement template search | | |
| TASK-343 | Add "Save as Template" option in designer | | |
| TASK-344 | Create template submission form | | |
| TASK-345 | Validate template before saving | | |
| TASK-346 | Store templates in backend or local storage | | |
| TASK-347 | Add template tags for categorization | | |
| TASK-348 | Test template creation workflow | | |

**Acceptance Criteria:**
- ✅ Templates gallery displays all templates
- ✅ Templates can be previewed before use
- ✅ Using template creates new workflow
- ✅ Users can save custom templates
- ✅ Templates are validated and stored correctly
- ✅ Search and categories work properly

---

## 3. Dependencies

### Additional Dependencies

- **DEP-020**: `sonner` or `react-hot-toast` for toast notifications
- **DEP-021**: `html-to-image` for canvas thumbnails
- **DEP-022**: `monaco-editor-react` for advanced code editing (optional)
- **DEP-023**: `framer-motion` for animations (optional)

### Backend Dependencies

- **DEP-024**: Backend must implement `/workflows/execute` endpoint
- **DEP-025**: Backend must support execution cancellation
- **DEP-026**: Backend must return execution metrics

---

## 4. Files

### New Component Files

- **FILE-029**: `components/ExecutionPanel.tsx` - Execution interface
- **FILE-030**: `components/QueueEditor.tsx` - Queue configuration
- **FILE-031**: `components/KeyboardShortcutsDialog.tsx` - Shortcuts help
- **FILE-032**: `components/ThemeToggle.tsx` - Dark mode toggle
- **FILE-033**: `components/TemplateGallery.tsx` - Templates display
- **FILE-034**: `components/TemplateCard.tsx` - Template preview
- **FILE-035**: `components/ErrorBoundary.tsx` - Error handling
- **FILE-036**: `components/LoadingState.tsx` - Loading skeletons

### Updated Files

- **FILE-037**: `lib/stores/useWorkflowStore.ts` - Add history, queues
- **FILE-038**: `lib/api.ts` - Add execute endpoint
- **FILE-039**: `lib/utils.ts` - Add keyboard shortcuts, thumbnails
- **FILE-040**: `app/page.tsx` - Enhanced dashboard

---

## 5. Success Criteria

✅ **Phase 2 is complete when:**

1. User can execute workflows with test input
2. Execution progress displays in real-time
3. Execution results show with full metrics
4. Queues can be configured with bandwidth settings
5. Queue visualization appears on canvas
6. Undo/redo works for all operations
7. All keyboard shortcuts function correctly
8. Dark mode is fully implemented and consistent
9. Toast notifications appear for all actions
10. Error handling is comprehensive and user-friendly
11. Dashboard search and filter work smoothly
12. Workflow thumbnails generate correctly
13. Workflow duplication creates valid copies
14. Recent and pinned workflows sections work
15. Templates gallery displays and works
16. Users can create custom templates
17. All P1 features are implemented and tested
18. Performance meets defined targets
19. UX is polished and intuitive
20. Ready for Phase 3 (Optimization & Advanced Features)

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Status:** Ready for Implementation  
**Total New Tasks:** 162 (Tasks 187-348)
