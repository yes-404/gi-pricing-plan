---
title: Use flushPromises for Testing Async Components
impact: HIGH
impactDescription: Without awaiting async operations, tests make assertions before the component has rendered, causing false negatives
type: gotcha
tags: [vue3, testing, async, defineAsyncComponent, flushPromises, vitest]
---

# Use flushPromises for Testing Async Components

**Impact: HIGH** - When testing async components created with `defineAsyncComponent`, you must use `await flushPromises()` to ensure the component has loaded before making assertions. Vue updates asynchronously, so tests that don't account for this will make assertions before the component has rendered.

## Task Checklist

- [ ] Use `async/await` in test functions for async components
- [ ] Call `await flushPromises()` after mounting async components
- [ ] Test loading states by making assertions before `flushPromises()`
- [ ] Test error states using rejected promises in `defineAsyncComponent`
- [ ] Use `trigger()` with `await` as it returns a Promise

**Incorrect:**

```javascript
import { mount } from '@vue/test-utils'
import { defineAsyncComponent } from 'vue'

const AsyncWidget = defineAsyncComponent(() =>
  import('./Widget.vue')
)

test('renders async component', () => {
  const wrapper = mount(AsyncWidget)

  // FAILS: Component hasn't loaded yet
  expect(wrapper.text()).toContain('Widget Content')
})
```

**Correct:**

```javascript
import { mount, flushPromises } from '@vue/test-utils'
import { defineAsyncComponent, nextTick } from 'vue'

const AsyncWidget = defineAsyncComponent(() =>
  import('./Widget.vue')
)

test('renders async component', async () => {
  const wrapper = mount(AsyncWidget)

  // Wait for async component to load
  await flushPromises()

  expect(wrapper.text()).toContain('Widget Content')
})

test('shows loading state initially', async () => {
  const AsyncWithLoading = defineAsyncComponent({
    loader: () => import('./Widget.vue'),
    loadingComponent: { template: '<div>Loading...</div>' },
    delay: 0
  })

  const wrapper = mount(AsyncWithLoading)

  // Check loading state immediately
  expect(wrapper.text()).toContain('Loading...')

  // Wait for component to load
  await flushPromises()

  // Check final state
  expect(wrapper.text()).toContain('Widget Content')
})
```

## Testing with Suspense

```javascript
import { mount, flushPromises } from '@vue/test-utils'
import { Suspense, defineAsyncComponent, h } from 'vue'

const AsyncWidget = defineAsyncComponent(() =>
  import('./Widget.vue')
)

test('renders async component with Suspense', async () => {
  const wrapper = mount({
    components: { AsyncWidget },
    template: `
      <Suspense>
        <AsyncWidget />
        <template #fallback>
          <div>Loading...</div>
        </template>
      </Suspense>
    `
  })

  // Initially shows fallback
  expect(wrapper.text()).toContain('Loading...')

  // Wait for async resolution
  await flushPromises()

  // Now shows actual content
  expect(wrapper.text()).toContain('Widget Content')
})
```

## Testing Error States

```javascript
import { mount, flushPromises } from '@vue/test-utils'
import { defineAsyncComponent } from 'vue'

test('shows error component on load failure', async () => {
  const AsyncWithError = defineAsyncComponent({
    loader: () => Promise.reject(new Error('Failed to load')),
    errorComponent: { template: '<div>Error loading component</div>' }
  })

  const wrapper = mount(AsyncWithError)

  await flushPromises()

  expect(wrapper.text()).toContain('Error loading component')
})
```

## A `waitFor` on synchronously-rendered content is not waiting

**Impact: HIGH — this one is silent.** It produces tests that pass, look like coverage, and
assert nothing.

A component that renders *some* content synchronously and fetches the rest in `onMounted`
has two populations on screen at different times. A `waitFor` gated on the synchronous half
resolves on the **first** check, before the fetch has settled — so every assertion after it
runs against a DOM the async data has not reached.

That is harmless for a presence assertion, which simply waits again. It is fatal for an
**absence** assertion, which is satisfied by the data not having arrived yet:

```ts
// WRONG. The four builtin <option>s render synchronously, so this waitFor resolves
// immediately and the absence below is true of a list that is still loading.
await waitFor(() => expect(options()).toContain("count:poisson"))
expect(options().join(" ")).not.toContain("excluded-item")   // vacuous
```

Found in W6b-4b, where it hid three of a component's four filtering rules: mutations that
deleted the status filter, the response filter and the backend filter **all passed**. The
suite was green and three properties were untested.

**Gate on something that can only appear after the fetch** — a control item in the same
fixture that the filter under test must let through:

```ts
// RIGHT. `visible-control` cannot render until the fetch resolves, so reaching the next
// line proves the async data is on screen and the absence means what it says.
listObjectives.mockResolvedValue({ items: [control(), excludedItem()] })
await waitFor(() => expect(options().join(" ")).toContain("visible-control"))
expect(options().join(" ")).not.toContain("excluded-item")
```

Where no control is possible — a case where *nothing* async may render — synchronise on the
mock having been called and settled, then assert:

```ts
await waitFor(() => expect(listObjectives).toHaveBeenCalled())
await Promise.resolve()
```

**Rule of thumb:** an absence assertion needs a presence assertion before it, and that
presence must be something the async path alone can produce. Waiting for something that was
already on screen is not waiting.

The general lesson is that this class of bug is invisible to a passing suite — it is only
detectable by breaking the code and checking the test notices. Run the mutation before
trusting the coverage.

## Utilities Reference

| Utility | Purpose |
|---------|---------|
| `await flushPromises()` | Resolves all pending promises |
| `await nextTick()` | Waits for Vue's next DOM update cycle |
| `await wrapper.trigger('click')` | Triggers event and waits for update |

## Dynamic Import Handling

**Note:** Dynamic imports (`import('./File.vue')`) may require additional handling beyond `flushPromises()` in test environments. Test runners like Vitest handle module resolution differently than runtime bundlers, which can cause timing issues with dynamic imports. If `flushPromises()` alone doesn't resolve the component, consider:

- Mocking the dynamic import to return the component synchronously
- Using multiple `await flushPromises()` calls in sequence
- Wrapping assertions in `waitFor()` or retry utilities
- Configuring your test runner's module resolution settings

```javascript
// If flushPromises() isn't sufficient, mock the import
vi.mock('./Widget.vue', () => ({
  default: { template: '<div>Widget Content</div>' }
}))

// Or use multiple flush calls for nested async operations
await flushPromises()
await flushPromises()
```

## References

- [Vue Test Utils - Asynchronous Behavior](https://test-utils.vuejs.org/guide/advanced/async-suspense)
- [Vue.js Async Components Documentation](https://vuejs.org/guide/components/async)
