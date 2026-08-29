import React from 'react';
import { CheckCircle, Clock, AlertCircle, FileCheck, Send, Circle } from 'lucide-react';

const STATUS_CONFIG = {
  completed: {
    label: 'Completed',
    icon: CheckCircle,
    bg: 'bg-emerald-50 text-emerald-800 border-emerald-300/80',
    iconColor: 'text-emerald-700',
  },
  under_review: {
    label: 'Under Review',
    icon: Clock,
    bg: 'bg-blue-50 text-blue-800 border-blue-200',
    iconColor: 'text-blue-700',
  },
  action_required: {
    label: 'Action Required',
    icon: AlertCircle,
    bg: 'bg-amber-50 text-amber-900 border-amber-300',
    iconColor: 'text-amber-700',
  },
  ready: {
    label: 'Ready',
    icon: FileCheck,
    bg: 'bg-indigo-50 text-indigo-800 border-indigo-200',
    iconColor: 'text-indigo-700',
  },
  submitted: {
    label: 'Submitted',
    icon: Send,
    bg: 'bg-sky-50 text-sky-800 border-sky-200',
    iconColor: 'text-sky-700',
  },
  not_started: {
    label: 'Not Started',
    icon: Circle,
    bg: 'bg-slate-100 text-slate-700 border-slate-300/70',
    iconColor: 'text-slate-500',
  },
};

export default function StatusBadge({ status = 'not_started', size = 'md' }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.not_started;
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs font-medium',
    lg: 'px-3 py-1.5 text-sm font-semibold',
  }[size] || 'px-2.5 py-1 text-xs font-medium';

  return (
    <span
      className={`inline-flex items-center space-x-1.5 rounded-md border ${config.bg} ${sizeClasses}`}
      title={`Status: ${config.label}`}
    >
      <Icon className={`w-3.5 h-3.5 shrink-0 ${config.iconColor}`} />
      <span>{config.label}</span>
    </span>
  );
}
