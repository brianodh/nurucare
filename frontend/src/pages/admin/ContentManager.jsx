import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  RefreshCw,
  Plus,
  Pencil,
  Trash2,
  Save,
} from 'lucide-react';
import {
  listContentItems,
  upsertContentItem,
  deleteContentItem,
} from '@/api/apiClient';

const TABS = [
  { value: 'myths', label: 'Myths', contentType: 'myths', displayField: 'myth_statement' },
  { value: 'who_guidelines', label: 'WHO Guidelines', contentType: 'who_guidelines', displayField: 'title' },
  { value: 'educational_content', label: 'Educational Content', contentType: 'educational_content', displayField: 'name' },
];

const getDisplayField = (contentType) => {
  const tab = TABS.find((t) => t.contentType === contentType);
  return tab?.displayField || 'title';
};

const getTitleForType = (item) => {
  const displayField = getDisplayField(item.content_type);
  const data = item.content_data || {};
  return (
    data[displayField] ||
    data.title ||
    data.name ||
    data.myth_statement ||
    item.item_key
  );
};

const prettifyJson = (obj) => {
  try {
    if (typeof obj === 'string') {
      return JSON.stringify(JSON.parse(obj), null, 2);
    }
    return JSON.stringify(obj, null, 2);
  } catch {
    return typeof obj === 'string' ? obj : '{}';
  }
};

const parseJson = (str) => {
  try {
    return JSON.parse(str);
  } catch {
    return null;
  }
};

export default function ContentManager() {
  const [activeTab, setActiveTab] = useState('myths');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [editContentJson, setEditContentJson] = useState('');

  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newItemKey, setNewItemKey] = useState('');
  const [newContentJson, setNewContentJson] = useState('{}');
  const [addParseError, setAddParseError] = useState(null);
  const [editParseError, setEditParseError] = useState(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingItem, setDeletingItem] = useState(null);

  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const activeTabConfig = TABS.find((t) => t.value === activeTab);
  const activeContentType = activeTabConfig?.contentType || 'myths';

  const fetchItems = async (contentType) => {
    setLoading(true);
    setError(null);
    try {
      const result = await listContentItems(contentType);
      const list = Array.isArray(result)
        ? result
        : result?.items || result?.data || [];
      const filtered = list.filter((it) => it.content_type === contentType);
      setItems(filtered);
    } catch (err) {
      console.error('Failed to load content items:', err);
      setError('Failed to load content items. Please try again.');
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems(activeContentType);
  }, [activeContentType]);

  const handleRefresh = () => {
    fetchItems(activeContentType);
  };

  const handleTabChange = (value) => {
    setActiveTab(value);
  };

  const openEditDialog = (item) => {
    setEditingItem(item);
    setEditContentJson(prettifyJson(item.content_data || {}));
    setEditParseError(null);
    setEditDialogOpen(true);
  };

  const handleEditSave = async () => {
    if (!editingItem) return;
    const parsed = parseJson(editContentJson);
    if (parsed === null) {
      setEditParseError('Invalid JSON. Please check your syntax.');
      return;
    }
    setSaving(true);
    try {
      await upsertContentItem(editingItem.content_type, editingItem.item_key, parsed);
      setEditDialogOpen(false);
      setEditingItem(null);
      fetchItems(activeContentType);
    } catch (err) {
      console.error('Failed to save item:', err);
      setEditParseError('Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const openAddDialog = () => {
    setNewItemKey('');
    setNewContentJson('{\n  \n}');
    setAddParseError(null);
    setAddDialogOpen(true);
  };

  const handleAddSave = async () => {
    if (!newItemKey.trim()) {
      setAddParseError('Item key is required.');
      return;
    }
    const parsed = parseJson(newContentJson);
    if (parsed === null) {
      setAddParseError('Invalid JSON. Please check your syntax.');
      return;
    }
    setSaving(true);
    try {
      await upsertContentItem(activeContentType, newItemKey.trim(), parsed);
      setAddDialogOpen(false);
      setNewItemKey('');
      setNewContentJson('{}');
      fetchItems(activeContentType);
    } catch (err) {
      console.error('Failed to create item:', err);
      setAddParseError('Failed to create item. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const openDeleteDialog = (item) => {
    setDeletingItem(item);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingItem) return;
    setDeleting(true);
    try {
      await deleteContentItem(deletingItem.content_type, deletingItem.item_key);
      setDeleteDialogOpen(false);
      setDeletingItem(null);
      fetchItems(activeContentType);
    } catch (err) {
      console.error('Failed to delete item:', err);
    } finally {
      setDeleting(false);
    }
  };

  const renderTable = (contentType) => {
    const filteredItems = items.filter((it) => it.content_type === contentType);

    if (loading) {
      return (
        <div className="flex items-center justify-center py-12 text-muted-foreground">
          <RefreshCw className="h-5 w-5 animate-spin mr-2" />
          Loading items...
        </div>
      );
    }

    if (error) {
      return (
        <div className="py-12 text-center">
          <p className="text-destructive mb-4">{error}</p>
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      );
    }

    if (filteredItems.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <p className="text-muted-foreground text-sm mb-4">
            No items of this type yet.
          </p>
          <Button variant="outline" size="sm" onClick={openAddDialog}>
            <Plus className="h-4 w-4 mr-2" />
            Add first item
          </Button>
        </div>
      );
    }

    return (
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Item Key</TableHead>
              <TableHead>{activeTabConfig?.displayField === 'myth_statement' ? 'Myth' : activeTabConfig?.displayField === 'name' ? 'Name' : 'Title'}</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Updated</TableHead>
              <TableHead>Updated By</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((item) => (
              <TableRow key={`${item.content_type}-${item.item_key}`}>
                <TableCell className="font-mono text-xs">
                  {item.item_key}
                </TableCell>
                <TableCell className="max-w-md truncate">
                  {getTitleForType(item)}
                </TableCell>
                <TableCell>
                  {item.version != null ? (
                    <Badge variant="outline">v{item.version}</Badge>
                  ) : (
                    <span className="text-muted-foreground text-xs">—</span>
                  )}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {item.updated_at ? String(item.updated_at).slice(0, 16) : '—'}
                </TableCell>
                <TableCell className="text-xs">
                  {item.updated_by ? (
                    <Badge variant="secondary" className="font-normal">
                      {item.updated_by}
                    </Badge>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditDialog(item)}
                      title="Edit"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openDeleteDialog(item)}
                      title="Delete"
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Content Manager</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage myths, WHO guidelines and educational content.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={openAddDialog}>
            <Plus className="h-4 w-4 mr-2" />
            Add Item
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Content Items</CardTitle>
          <CardDescription>
            Switch between tabs to manage different types of content.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={handleTabChange}>
            <TabsList className="grid grid-cols-3 mb-6 w-full sm:w-auto sm:inline-flex">
              {TABS.map((tab) => (
                <TabsTrigger key={tab.value} value={tab.value}>
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>
            {TABS.map((tab) => (
              <TabsContent key={tab.value} value={tab.value}>
                {renderTable(tab.contentType)}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Content Item</DialogTitle>
            <DialogDescription>
              Edit the JSON content data for <span className="font-mono font-semibold">{editingItem?.item_key}</span>
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Item Key</label>
              <Input value={editingItem?.item_key || ''} readOnly disabled />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Content Type</label>
              <Input value={editingItem?.content_type || ''} readOnly disabled />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Content Data (JSON)</label>
                <span className="text-xs text-muted-foreground">
                  {activeTabConfig && (
                    <>Tip: include <code className="font-mono bg-muted px-1 rounded">"{activeTabConfig.displayField}"</code> field</>
                  )}
                </span>
              </div>
              <Textarea
                value={editContentJson}
                onChange={(e) => {
                  setEditContentJson(e.target.value);
                  if (editParseError) setEditParseError(null);
                }}
                rows={14}
                className="font-mono text-xs"
              />
              {editParseError && (
                <p className="text-xs text-destructive">{editParseError}</p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)} disabled={saving}>
              Cancel
            </Button>
            <Button onClick={handleEditSave} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add New Content Item</DialogTitle>
            <DialogDescription>
              Create a new {activeTabConfig?.label?.toLowerCase()} content item.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Item Key</label>
              <Input
                value={newItemKey}
                onChange={(e) => {
                  setNewItemKey(e.target.value);
                  if (addParseError) setAddParseError(null);
                }}
                placeholder="e.g. myth_01 or contraception_intro"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Content Type</label>
              <Input value={activeContentType} readOnly disabled />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Content Data (JSON)</label>
                <span className="text-xs text-muted-foreground">
                  {activeTabConfig && (
                    <>Tip: include <code className="font-mono bg-muted px-1 rounded">"{activeTabConfig.displayField}"</code> field</>
                  )}
                </span>
              </div>
              <Textarea
                value={newContentJson}
                onChange={(e) => {
                  setNewContentJson(e.target.value);
                  if (addParseError) setAddParseError(null);
                }}
                rows={14}
                className="font-mono text-xs"
              />
              {addParseError && (
                <p className="text-xs text-destructive">{addParseError}</p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddDialogOpen(false)} disabled={saving}>
              Cancel
            </Button>
            <Button onClick={handleAddSave} disabled={saving}>
              <Plus className="h-4 w-4 mr-2" />
              {saving ? 'Creating...' : 'Create Item'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Content Item</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{' '}
              <span className="font-mono font-semibold">{deletingItem?.item_key}</span>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={deleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {deleting ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
