import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Calendar, FileText, Briefcase, CheckCheck, Check } from 'lucide-react';
import notificationsApi from '../../api/notificationsApi';
import { useAuth } from '../../context/AuthContext';

export const NotificationBell = ({ onOpen }) => {
  const { isAuthenticated, isEmployer, isJobSeeker } = useAuth();
  const navigate = useNavigate();

  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const fetchUnreadCount = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await notificationsApi.getUnreadCount();
      setUnreadCount(typeof data?.unread_count === 'number' ? data.unread_count : 0);
    } catch {
      // Silently ignore background polling errors
    }
  }, [isAuthenticated]);

  const fetchNotifications = useCallback(async () => {
    if (!isAuthenticated) return;
    setIsLoading(true);
    try {
      const data = await notificationsApi.getNotifications();
      const list = Array.isArray(data) ? data : (data?.results || []);
      setNotifications(list);
      const unread = list.filter((n) => !n.is_read).length;
      if (Array.isArray(data)) {
        setUnreadCount(unread);
      } else {
        fetchUnreadCount();
      }
    } catch {
      // Keep previous list on error
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, fetchUnreadCount]);

  useEffect(() => {
    if (!isAuthenticated) {
      setNotifications([]);
      setUnreadCount(0);
      return;
    }
    fetchUnreadCount();
    const intervalId = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(intervalId);
  }, [isAuthenticated, fetchUnreadCount]);

  const handleToggle = () => {
    const nextOpen = !isOpen;
    setIsOpen(nextOpen);
    if (nextOpen) {
      if (onOpen) onOpen();
      fetchNotifications();
    }
  };

  const getTargetRoute = (notif) => {
    if (notif.notification_type === 'interview_scheduled') {
      return isEmployer ? '/employer/interviews' : '/interviews';
    }
    if (notif.notification_type === 'application_update') {
      return isEmployer ? '/employer/jobs' : '/applications';
    }
    if (notif.notification_type === 'new_job_match') {
      return '/jobs';
    }
    return isJobSeeker ? '/applications' : '/employer/dashboard';
  };

  const handleNotificationClick = async (notif) => {
    if (!notif.is_read) {
      try {
        await notificationsApi.markAsRead(notif.id);
        setNotifications((prev) =>
          prev.map((item) => (item.id === notif.id ? { ...item, is_read: true } : item))
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
      } catch {
        // Proceed with navigation even if mark-read fails
      }
    }
    setIsOpen(false);
    navigate(getTargetRoute(notif));
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      setNotifications((prev) => prev.map((item) => ({ ...item, is_read: true })));
      setUnreadCount(0);
    } catch {
      // Ignore error
    }
  };

  const renderIcon = (type) => {
    switch (type) {
      case 'interview_scheduled':
        return <Calendar className="w-4 h-4 text-wine-burgundy" />;
      case 'application_update':
        return <FileText className="w-4 h-4 text-wine-deep" />;
      case 'new_job_match':
        return <Briefcase className="w-4 h-4 text-emerald-700" />;
      default:
        return <Bell className="w-4 h-4 text-ink-muted" />;
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="relative">
      <button
        type="button"
        onClick={handleToggle}
        aria-label="Notifications"
        className="relative p-2 rounded-xl border border-sand-border hover:border-wine-burgundy bg-white text-ink-charcoal hover:text-wine-deep transition-all shadow-xs"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 rounded-full bg-wine-deep text-white text-[10px] font-bold flex items-center justify-center shadow-xs">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-20"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-wine-lg border border-sand-border z-30 overflow-hidden">
            <div className="px-4 py-3 border-b border-sand-border flex items-center justify-between bg-sand-canvas/40">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-wine-deep">
                  Notifications
                </span>
                {unreadCount > 0 && (
                  <span className="px-1.5 py-0.5 rounded-full bg-wine-tint text-wine-deep text-[10px] font-bold">
                    {unreadCount} new
                  </span>
                )}
              </div>
              {unreadCount > 0 && (
                <button
                  type="button"
                  onClick={handleMarkAllRead}
                  className="inline-flex items-center gap-1 text-[11px] font-semibold text-wine-burgundy hover:text-wine-deep transition-colors"
                >
                  <CheckCheck className="w-3.5 h-3.5" /> Mark all read
                </button>
              )}
            </div>

            <div className="max-h-96 overflow-y-auto divide-y divide-sand-border/60">
              {isLoading ? (
                <div className="p-6 text-center text-xs text-ink-muted">
                  Loading notifications...
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-8 text-center space-y-2">
                  <Bell className="w-7 h-7 text-wine-burgundy/40 mx-auto" />
                  <p className="text-xs font-semibold text-ink-charcoal">
                    You're all caught up
                  </p>
                  <p className="text-[11px] text-ink-subtle">
                    Status updates and scheduled interviews will appear here.
                  </p>
                </div>
              ) : (
                notifications.map((notif) => (
                  <button
                    key={notif.id}
                    type="button"
                    onClick={() => handleNotificationClick(notif)}
                    className={`w-full text-left px-4 py-3 flex items-start gap-3 transition-colors hover:bg-sand-canvas/50 ${
                      !notif.is_read ? 'bg-wine-tint/25' : 'bg-white'
                    }`}
                  >
                    <div className="w-8 h-8 rounded-lg bg-sand-canvas border border-sand-border flex items-center justify-center flex-shrink-0 mt-0.5">
                      {renderIcon(notif.notification_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <p className={`text-xs truncate ${!notif.is_read ? 'font-bold text-ink-charcoal' : 'font-medium text-ink-muted'}`}>
                          {notif.title}
                        </p>
                        {!notif.is_read ? (
                          <span className="w-2 h-2 rounded-full bg-wine-deep flex-shrink-0" title="Unread" />
                        ) : (
                          <Check className="w-3 h-3 text-ink-subtle flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-[11px] text-ink-muted mt-0.5 line-clamp-2">
                        {notif.message}
                      </p>
                      <p className="text-[10px] text-ink-subtle mt-1">
                        {new Date(notif.created_at).toLocaleString()}
                      </p>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationBell;
