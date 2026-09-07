import { visit } from 'unist-util-visit';

export function remarkBaseUrl(base) {
  const prefix = base.replace(/\/$/, '');
  return (tree) => {
    visit(tree, 'image', (node) => {
      if (node.url && node.url.startsWith('/') && !node.url.startsWith(prefix + '/')) {
        node.url = prefix + node.url;
      }
    });
    visit(tree, 'link', (node) => {
      if (node.url && node.url.startsWith('/') && !node.url.startsWith(prefix + '/')) {
        node.url = prefix + node.url;
      }
    });
  };
}
