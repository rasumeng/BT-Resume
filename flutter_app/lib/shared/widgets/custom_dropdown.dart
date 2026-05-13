import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path/path.dart' as p;

import '../../config/colors.dart';
import '../../config/typography.dart';

class CustomResumeDropdown extends StatefulWidget {
  const CustomResumeDropdown({
    super.key,
    required this.resumeFiles,
    required this.selectedIndex,
    required this.onChanged,
  });

  final List<File> resumeFiles;
  final int selectedIndex;
  final ValueChanged<int> onChanged;

  @override
  State<CustomResumeDropdown> createState() => _CustomResumeDropdownState();
}

class _CustomResumeDropdownState extends State<CustomResumeDropdown> {
  final LayerLink _layerLink = LayerLink();
  final GlobalKey _triggerKey = GlobalKey();
  OverlayEntry? _overlayEntry;
  bool _isOpen = false;

  @override
  void dispose() {
    _removeOverlay();
    super.dispose();
  }

  void _toggleDropdown() {
    if (_isOpen) {
      _closeDropdown();
    } else {
      _openDropdown();
    }
  }

  void _openDropdown() {
    if (_isOpen || widget.resumeFiles.isEmpty) return;

    final overlay = Overlay.of(context);
    if (overlay == null) return;

    setState(() {
      _isOpen = true;
    });

    _overlayEntry = OverlayEntry(
      builder: (context) {
        final renderBox = _triggerKey.currentContext?.findRenderObject() as RenderBox?;
        final triggerSize = renderBox?.size ?? const Size(200, 44);

        return Stack(
          children: [
            Positioned.fill(
              child: GestureDetector(
                behavior: HitTestBehavior.translucent,
                onTap: _closeDropdown,
              ),
            ),
            CompositedTransformFollower(
              link: _layerLink,
              offset: Offset(0, triggerSize.height + 4),
              showWhenUnlinked: false,
              child: Material(
                color: Colors.transparent,
                child: TweenAnimationBuilder<double>(
                  duration: const Duration(milliseconds: 200),
                  curve: Curves.easeInOut,
                  tween: Tween<double>(begin: 0, end: 1),
                  builder: (context, value, child) {
                    return Opacity(
                      opacity: value,
                      child: Transform.scale(
                        scaleY: 0.96 + (0.04 * value),
                        alignment: Alignment.topCenter,
                        child: child,
                      ),
                    );
                  },
                  child: Container(
                    width: triggerSize.width,
                    constraints: const BoxConstraints(maxHeight: 200),
                    decoration: BoxDecoration(
                      color: AppColors.dark2,
                      border: Border.all(color: AppColors.gold.withOpacity(0.3)),
                      borderRadius: BorderRadius.circular(8),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.25),
                          blurRadius: 12,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: ListView.builder(
                        padding: EdgeInsets.zero,
                        shrinkWrap: true,
                        itemCount: widget.resumeFiles.length,
                        itemBuilder: (context, index) {
                          return _DropdownItem(
                            filename: p.basename(widget.resumeFiles[index].path),
                            isSelected: widget.selectedIndex == index,
                            onTap: () {
                              widget.onChanged(index);
                              _closeDropdown();
                            },
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );

    overlay.insert(_overlayEntry!);
  }

  void _closeDropdown() {
    if (!_isOpen) return;
    _removeOverlay();
    if (mounted) {
      setState(() {
        _isOpen = false;
      });
    }
  }

  void _removeOverlay() {
    _overlayEntry?.remove();
    _overlayEntry = null;
  }

  @override
  Widget build(BuildContext context) {
    final hasItems = widget.resumeFiles.isNotEmpty;
    final selectedFileName = hasItems && widget.selectedIndex < widget.resumeFiles.length
        ? p.basename(widget.resumeFiles[widget.selectedIndex].path)
        : 'No resumes available';

    return CompositedTransformTarget(
      link: _layerLink,
      child: GestureDetector(
        key: _triggerKey,
        onTap: hasItems ? _toggleDropdown : null,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeInOut,
          height: 44,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            color: AppColors.dark3,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: AppColors.dark2),
          ),
          child: Row(
            children: [
              Icon(
                Icons.picture_as_pdf,
                color: AppColors.errorRed,
                size: 16,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  selectedFileName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: AppTypography.bodySmall.copyWith(
                    color: hasItems ? AppColors.cream : AppColors.textSecondary,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              AnimatedRotation(
                turns: _isOpen ? 0.5 : 0,
                duration: const Duration(milliseconds: 200),
                curve: Curves.easeInOut,
                child: Icon(
                  Icons.keyboard_arrow_down,
                  color: AppColors.gold,
                  size: 20,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DropdownItem extends StatefulWidget {
  const _DropdownItem({
    required this.filename,
    required this.isSelected,
    required this.onTap,
  });

  final String filename;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  State<_DropdownItem> createState() => _DropdownItemState();
}

class _DropdownItemState extends State<_DropdownItem> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: Container(
          height: 44,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          color: _isHovered ? AppColors.dark3 : Colors.transparent,
          child: Row(
            children: [
              Icon(
                Icons.picture_as_pdf,
                color: AppColors.errorRed,
                size: 16,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  widget.filename,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.cream,
                  ),
                ),
              ),
              if (widget.isSelected)
                Icon(
                  Icons.check,
                  color: AppColors.gold,
                  size: 16,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
