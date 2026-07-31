import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  listAdminUsers,
  adminCreateNurse,
  adminUpdateUserRole,
  adminToggleUserActive,
} from '@/api/apiClient';
import { useAuth } from '@/lib/AuthContext';
import { useToast } from '@/components/ui/use-toast';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Search,
  RefreshCw,
  Plus,
  UserPlus,
  ShieldAlert,
  UserCog,
  UserCheck,
  UserX,
} from 'lucide-react';

const roleBadgeClass = {
  patient: 'bg-sky-500/10 text-sky-700 border-sky-500/30',
  nurse: 'bg-emerald-500/10 text-emerald-700 border-emerald-500/30',
  admin: 'bg-indigo-500/10 text-indigo-700 border-indigo-500/30',
};

const passwordValidation = (pw) => {
  if (!pw || pw.length < 8) return 'Password must be at least 8 characters.';
  if (!/\d/.test(pw)) return 'Password must contain at least 1 digit.';
  return null;
};

const formatCreatedAt = (v) => {
  if (!v) return '—';
  try {
    return new Date(v).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
    });
  } catch {
    return '—';
  }
};

export default function UserManagement() {
  const { user: currentAuthUser } = useAuth();
  const { toast } = useToast();

  const [role, setRole] = useState('all');
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const debounceRef = useRef(null);

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    gender: '',
    institution_name: '',
    institution_address: '',
  });

  const fetchUsers = useCallback(async () => {
    try {
      setError(false);
      const effectiveRole = role === 'all' ? null : role;
      const effectiveSearch = debouncedSearch.trim() || null;
      const res = await listAdminUsers(effectiveRole, effectiveSearch);
      const list = Array.isArray(res) ? res : res?.users || [];
      setUsers(list);
    } catch (e) {
      setError(true);
      setUsers([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [role, debouncedSearch]);

  useEffect(() => {
    setLoading(true);
    fetchUsers();
  }, [fetchUsers]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedSearch(searchInput);
    }, 400);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [searchInput]);

  const handleRefresh = () => {
    setRefreshing(true);
    setLoading(true);
    fetchUsers();
  };

  const handleResetFilters = () => {
    setRole('all');
    setSearchInput('');
    setDebouncedSearch('');
  };

  const handleRoleChange = async (user_id, new_role) => {
    try {
      await adminUpdateUserRole(user_id, new_role);
      setUsers((prev) =>
        prev.map((u) =>
          (u.id === user_id || u.user_id === user_id) ? { ...u, role: new_role } : u
        )
      );
      toast({
        title: 'Role updated',
        description: `User role changed to ${new_role}.`,
      });
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Could not update role.';
      toast({
        variant: 'destructive',
        title: 'Update failed',
        description: msg,
      });
    }
  };

  const handleToggleActive = async (row) => {
    const id = row.id || row.user_id;
    const next_active = !row.is_active;
    try {
      await adminToggleUserActive(id, next_active);
      setUsers((prev) =>
        prev.map((u) =>
          (u.id === id || u.user_id === id) ? { ...u, is_active: next_active } : u
        )
      );
      toast({
        title: next_active ? 'Account reactivated' : 'Account deactivated',
        description: `${row.username || row.email} is now ${next_active ? 'active' : 'inactive'}.`,
      });
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Could not update account.';
      toast({
        variant: 'destructive',
        title: 'Update failed',
        description: msg,
      });
    }
  };

  const isSelf = (row) => {
    if (!currentAuthUser) return false;
    const rowId = row.id || row.user_id;
    const authId = currentAuthUser.sub || currentAuthUser.id;
    const idMatch = rowId && authId && String(rowId) === String(authId);
    const usernameMatch =
      row.username &&
      currentAuthUser.username &&
      String(row.username).toLowerCase() === String(currentAuthUser.username).toLowerCase();
    return idMatch || usernameMatch;
  };

  const updateField = (k, v) => {
    setForm((prev) => ({ ...prev, [k]: v }));
    if (formErrors[k]) {
      setFormErrors((prev) => {
        const next = { ...prev };
        delete next[k];
        return next;
      });
    }
  };

  const validateForm = () => {
    const errs = {};
    if (!form.username.trim()) errs.username = 'Username is required.';
    if (!form.email.trim()) errs.email = 'Email is required.';
    else if (!/^\S+@\S+\.\S+$/.test(form.email)) errs.email = 'Enter a valid email.';
    const pwErr = passwordValidation(form.password);
    if (pwErr) errs.password = pwErr;
    if (!form.full_name.trim()) errs.full_name = 'Full name is required.';
    if (!form.gender) errs.gender = 'Gender is required.';
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleCreateNurse = async () => {
    if (!validateForm()) return;
    setFormSubmitting(true);
    try {
      await adminCreateNurse({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        full_name: form.full_name.trim(),
        gender: form.gender,
        institution_name: form.institution_name.trim() || null,
        institution_address: form.institution_address.trim() || null,
      });
      toast({
        title: 'Nurse account created',
        description: `${form.full_name} can now sign in.`,
      });
      setDialogOpen(false);
      setForm({
        username: '',
        email: '',
        password: '',
        full_name: '',
        gender: '',
        institution_name: '',
        institution_address: '',
      });
      setFormErrors({});
      setLoading(true);
      fetchUsers();
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Could not create nurse account.';
      toast({
        variant: 'destructive',
        title: 'Creation failed',
        description: msg,
      });
    } finally {
      setFormSubmitting(false);
    }
  };

  const selfTooltip = 'You cannot modify your own account.';

  return (
    <TooltipProvider delayDuration={200}>
      <div className="space-y-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="font-heading text-2xl font-bold">User Management</h1>
            <p className="text-muted-foreground text-sm mt-1">
              Manage platform accounts, roles and access.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="w-4 h-4" />
                  Create Nurse Account
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <UserPlus className="w-4 h-4" /> Create Nurse Account
                  </DialogTitle>
                  <DialogDescription>
                    Register a new nurse account. They can sign in immediately.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-2">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <Label htmlFor="um-username">Username *</Label>
                      <Input
                        id="um-username"
                        value={form.username}
                        onChange={(e) => updateField('username', e.target.value)}
                        placeholder="e.g. nurse.jane"
                      />
                      {formErrors.username && (
                        <p className="text-xs text-destructive">{formErrors.username}</p>
                      )}
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="um-email">Email *</Label>
                      <Input
                        id="um-email"
                        type="email"
                        value={form.email}
                        onChange={(e) => updateField('email', e.target.value)}
                        placeholder="name@clinic.org"
                      />
                      {formErrors.email && (
                        <p className="text-xs text-destructive">{formErrors.email}</p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <Label htmlFor="um-fullname">Full Name *</Label>
                      <Input
                        id="um-fullname"
                        value={form.full_name}
                        onChange={(e) => updateField('full_name', e.target.value)}
                        placeholder="Dr. Jane Doe"
                      />
                      {formErrors.full_name && (
                        <p className="text-xs text-destructive">{formErrors.full_name}</p>
                      )}
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="um-gender">Gender *</Label>
                      <Select value={form.gender} onValueChange={(v) => updateField('gender', v)}>
                        <SelectTrigger id="um-gender">
                          <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                      {formErrors.gender && (
                        <p className="text-xs text-destructive">{formErrors.gender}</p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="um-password">
                      Password * <span className="text-muted-foreground font-normal">(min 8 chars, at least 1 digit)</span>
                    </Label>
                    <Input
                      id="um-password"
                      type="password"
                      value={form.password}
                      onChange={(e) => updateField('password', e.target.value)}
                      placeholder="••••••••"
                    />
                    {formErrors.password && (
                      <p className="text-xs text-destructive">{formErrors.password}</p>
                    )}
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="um-inst-name">Institution Name</Label>
                    <Input
                      id="um-inst-name"
                      value={form.institution_name}
                      onChange={(e) => updateField('institution_name', e.target.value)}
                      placeholder="e.g. Marie Stopes Clinic"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="um-inst-addr">Institution Address</Label>
                    <Input
                      id="um-inst-addr"
                      value={form.institution_address}
                      onChange={(e) => updateField('institution_address', e.target.value)}
                      placeholder="Street, City"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setDialogOpen(false);
                      setFormErrors({});
                    }}
                    disabled={formSubmitting}
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleCreateNurse} disabled={formSubmitting}>
                    {formSubmitting ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Creating…
                      </>
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4" />
                        Create Nurse
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <Card className="rounded-2xl">
          <CardHeader className="pb-3">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="relative w-full sm:max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  className="pl-9"
                  placeholder="Search by username, email, or full name…"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                />
              </div>
              <Tabs value={role} onValueChange={setRole} className="w-full sm:w-auto">
                <TabsList className="w-full sm:w-auto grid grid-cols-4 sm:inline-flex">
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="patient">Patient</TabsTrigger>
                  <TabsTrigger value="nurse">Nurse</TabsTrigger>
                  <TabsTrigger value="admin">Admin</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </CardHeader>
          <CardContent>
            {error ? (
              <div className="py-14 text-center space-y-3">
                <p className="text-sm text-muted-foreground">Couldn&apos;t load users.</p>
                <Button variant="outline" size="sm" onClick={handleRefresh}>
                  <RefreshCw className="w-4 h-4" />
                  Retry
                </Button>
              </div>
            ) : loading ? (
              <div className="space-y-2">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="grid grid-cols-7 gap-3 py-3">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                ))}
              </div>
            ) : users.length === 0 ? (
              <div className="py-16 text-center space-y-3">
                <UserX className="w-10 h-10 mx-auto text-muted-foreground/40" />
                <p className="text-sm text-muted-foreground">No users found.</p>
                {(role !== 'all' || debouncedSearch) && (
                  <Button variant="link" size="sm" onClick={handleResetFilters}>
                    Reset filters
                  </Button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Username</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Full Name</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Created At</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((row) => {
                      const rowId = row.id || row.user_id;
                      const rowRole = row.role || 'patient';
                      const rowActive = row.is_active !== false;
                      const self = isSelf(row);
                      return (
                        <TableRow key={rowId}>
                          <TableCell className="font-medium">{row.username || '—'}</TableCell>
                          <TableCell className="text-muted-foreground">{row.email || '—'}</TableCell>
                          <TableCell>{row.full_name || '—'}</TableCell>
                          <TableCell>
                            <Badge variant="outline" className={roleBadgeClass[rowRole] || ''}>
                              <span className="capitalize">{rowRole}</span>
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {rowActive ? (
                              <Badge variant="outline" className="bg-green-500/10 text-green-700 border-green-500/30">
                                Active
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="bg-rose-500/10 text-rose-700 border-rose-500/30">
                                Inactive
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {formatCreatedAt(row.created_at)}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="inline-flex items-center gap-2 justify-end">
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span>
                                    <DropdownMenu>
                                      <DropdownMenuTrigger asChild>
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          className="gap-1"
                                          disabled={self}
                                          onClick={(e) => {
                                            if (self) e.preventDefault();
                                          }}
                                        >
                                          <UserCog className="w-4 h-4" />
                                          Role
                                        </Button>
                                      </DropdownMenuTrigger>
                                      <DropdownMenuContent align="end" className="w-48">
                                        <DropdownMenuLabel>Change role</DropdownMenuLabel>
                                        <DropdownMenuSeparator />
                                        {/*
                                          "Promote to Admin" intentionally removed.
                                          Admin accounts are created exclusively via
                                          the CLI bootstrap script
                                          (backend/scripts/create_admin.py) -- the
                                          API rejects role="admin" on this endpoint
                                          (see api/endpoints/admin.py:
                                          admin_update_role), so this action would
                                          only ever fail with a 403. Existing admins
                                          are still visible read-only via the Admin
                                          tab/filter above.
                                        */}
                                        <DropdownMenuItem
                                          disabled={rowRole === 'nurse'}
                                          onClick={() => handleRoleChange(rowId, 'nurse')}
                                        >
                                          <UserCheck className="w-4 h-4 text-emerald-600" />
                                          Set as Nurse
                                        </DropdownMenuItem>
                                        <DropdownMenuItem
                                          disabled={rowRole === 'patient'}
                                          onClick={() => handleRoleChange(rowId, 'patient')}
                                        >
                                          <ShieldAlert className="w-4 h-4 text-sky-600" />
                                          Demote to Patient
                                        </DropdownMenuItem>
                                      </DropdownMenuContent>
                                    </DropdownMenu>
                                  </span>
                                </TooltipTrigger>
                                {self && (
                                  <TooltipContent>{selfTooltip}</TooltipContent>
                                )}
                              </Tooltip>

                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className="inline-flex items-center gap-2">
                                    <Switch
                                      checked={rowActive}
                                      disabled={self}
                                      onCheckedChange={() => handleToggleActive(row)}
                                      aria-label={rowActive ? 'Deactivate account' : 'Reactivate account'}
                                    />
                                    <span className="text-xs text-muted-foreground hidden sm:inline">
                                      {rowActive ? 'Active' : 'Inactive'}
                                    </span>
                                  </span>
                                </TooltipTrigger>
                                {self && (
                                  <TooltipContent>{selfTooltip}</TooltipContent>
                                )}
                              </Tooltip>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </TooltipProvider>
  );
}