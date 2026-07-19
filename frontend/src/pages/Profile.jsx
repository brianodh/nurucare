import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, User, Mail, Calendar, Edit, Save, 
  CheckCircle, AlertCircle, LogOut 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { useAuth } from '@/lib/AuthContext';
import { useLang } from '@/lib/i18n.jsx';
import { useToast } from '@/components/ui/use-toast';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { t } = useLang();
  const { toast } = useToast();
  
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      // In real app, this would call an API to update user info
      // For now, just show a success toast
      toast({
        title: t('success'),
        description: 'Profile updated successfully!',
      });
      setIsEditing(false);
    } catch (err) {
      toast({
        title: t('error'),
        description: 'Failed to update profile',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-[85vh] py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="flex items-center gap-3 mb-6">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)} className="rounded-full">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-2xl font-bold font-heading">Profile</h1>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Profile Header */}
          <Card className="p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="w-10 h-10 text-primary" />
              </div>
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-3">
                    <div className="space-y-1.5">
                      <Label htmlFor="name">Name</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="Enter your name"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        placeholder="Enter your email"
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleSave} disabled={loading} className="gap-2">
                        {loading ? (
                          <><span className="animate-spin">⏳</span> Saving...</>
                        ) : (
                          <><Save className="w-4 h-4" /> Save</>
                        )}
                      </Button>
                      <Button variant="ghost" onClick={() => setIsEditing(false)}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <h2 className="text-xl font-semibold">{user?.name || 'User'}</h2>
                    <p className="text-muted-foreground flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      {user?.email || 'No email set'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Role: {user?.role || 'Patient'}
                    </p>
                    <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)} className="gap-2 mt-2">
                      <Edit className="w-4 h-4" /> Edit Profile
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Account Actions */}
          <Card className="p-6">
            <h3 className="font-semibold mb-4">Account Settings</h3>
            <div className="space-y-3">
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={handleLogout} 
                className="w-full justify-start gap-2"
              >
                <LogOut className="w-4 h-4" /> Log Out
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
