# @codewhisper/ui-components

Shared UI components for CodeWhisper PR.

## Installation

```bash
yarn add @codewhisper/ui-components
```

## Components

### Button
```tsx
import { Button } from '@codewhisper/ui-components';

<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>
```

### Card
```tsx
import { Card } from '@codewhisper/ui-components';

<Card title="Title" description="Description">
  <div>Content</div>
</Card>
```

### Input
```tsx
import { Input } from '@codewhisper/ui-components';

<Input
  type="text"
  placeholder="Enter text"
  value={value}
  onChange={handleChange}
/>
```

### Select
```tsx
import { Select } from '@codewhisper/ui-components';

<Select
  options={options}
  value={selected}
  onChange={handleSelect}
/>
```

## Development

```bash
yarn build
yarn type-check
```
